"""Detect environment variable references in source code."""

from __future__ import annotations

import re
from pathlib import Path

from preflight.models import EnvVar

# Regex patterns per language for env var extraction.
# Each pattern has a named group "name" for the variable name
# and optionally a named group "default" to detect if a default exists.

PYTHON_PATTERNS = [
    # os.getenv("VAR") or os.getenv("VAR", "default")
    re.compile(
        r"""os\.getenv\(\s*["'](?P<name>[A-Z_][A-Z0-9_]*)["']"""
        r"""(?:\s*,\s*(?P<default>[^)]+))?\s*\)""",
    ),
    # os.environ["VAR"]
    re.compile(r"""os\.environ\[["'](?P<name>[A-Z_][A-Z0-9_]*)["']\]"""),
    # os.environ.get("VAR") or os.environ.get("VAR", "default")
    re.compile(
        r"""os\.environ\.get\(\s*["'](?P<name>[A-Z_][A-Z0-9_]*)["']"""
        r"""(?:\s*,\s*(?P<default>[^)]+))?\s*\)""",
    ),
]

JS_PATTERNS = [
    # process.env.VAR_NAME
    re.compile(r"""process\.env\.(?P<name>[A-Z_][A-Z0-9_]*)"""),
    # process.env["VAR_NAME"]
    re.compile(r"""process\.env\[["'](?P<name>[A-Z_][A-Z0-9_]*)["']\]"""),
]

GO_PATTERNS = [
    # os.Getenv("VAR")
    re.compile(r"""os\.Getenv\(\s*["'](?P<name>[A-Z_][A-Z0-9_]*)["']\s*\)"""),
    # os.LookupEnv("VAR")
    re.compile(r"""os\.LookupEnv\(\s*["'](?P<name>[A-Z_][A-Z0-9_]*)["']\s*\)"""),
]

RUBY_PATTERNS = [
    # ENV["VAR"] or ENV['VAR']
    re.compile(r"""ENV\[["'](?P<name>[A-Z_][A-Z0-9_]*)["']\]"""),
    # ENV.fetch("VAR") or ENV.fetch("VAR", "default")
    re.compile(
        r"""ENV\.fetch\(\s*["'](?P<name>[A-Z_][A-Z0-9_]*)["']"""
        r"""(?:\s*,\s*(?P<default>[^)]+))?\s*\)""",
    ),
]

RUST_PATTERNS = [
    # std::env::var("VAR") or env::var("VAR")
    re.compile(r"""env::var\(\s*["'](?P<name>[A-Z_][A-Z0-9_]*)["']\s*\)"""),
    # std::env::var_os("VAR")
    re.compile(r"""env::var_os\(\s*["'](?P<name>[A-Z_][A-Z0-9_]*)["']\s*\)"""),
]

PHP_PATTERNS = [
    # getenv("VAR")
    re.compile(r"""getenv\(\s*["'](?P<name>[A-Z_][A-Z0-9_]*)["']\s*\)"""),
    # $_ENV["VAR"]
    re.compile(r"""\$_ENV\[["'](?P<name>[A-Z_][A-Z0-9_]*)["']\]"""),
    # $_SERVER["VAR"]
    re.compile(r"""\$_SERVER\[["'](?P<name>[A-Z_][A-Z0-9_]*)["']\]"""),
]

EXTENSION_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    ".py": PYTHON_PATTERNS,
    ".js": JS_PATTERNS,
    ".ts": JS_PATTERNS,
    ".tsx": JS_PATTERNS,
    ".jsx": JS_PATTERNS,
    ".mjs": JS_PATTERNS,
    ".cjs": JS_PATTERNS,
    ".go": GO_PATTERNS,
    ".rb": RUBY_PATTERNS,
    ".rs": RUST_PATTERNS,
    ".php": PHP_PATTERNS,
}

# Pattern for .env / .env.example files: KEY=value lines
DOTENV_PATTERN = re.compile(r"^(?P<name>[A-Z_][A-Z0-9_]*)=(?P<value>.*)$", re.MULTILINE)


def _scan_dotenv(path: Path, rel: str) -> list[EnvVar]:
    results = []
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return results

    seen: set[str] = set()
    for match in DOTENV_PATTERN.finditer(content):
        name = match.group("name")
        if name not in seen:
            seen.add(name)
            value = match.group("value").strip()
            has_default = bool(value) and value not in ('""', "''", "")
            results.append(EnvVar(name=name, source_file=rel, has_default=has_default))

    return results


def detect_envvars(root: Path, files: list[Path]) -> list[EnvVar]:
    """Scan source files for environment variable references.

    Also parses .env and .env.example files in the root directory.
    Returns a deduplicated list of env vars sorted alphabetically by name.
    """
    results: list[EnvVar] = []
    seen: set[str] = set()

    # Check for .env files in root
    for env_filename in (".env", ".env.example", ".env.sample", ".env.template"):
        env_path = root / env_filename
        if env_path.is_file():
            for var in _scan_dotenv(env_path, env_filename):
                if var.name not in seen:
                    seen.add(var.name)
                    results.append(var)

    # Scan source files
    for filepath in files:
        ext = filepath.suffix.lower()
        patterns = EXTENSION_PATTERNS.get(ext)
        if not patterns:
            continue

        try:
            content = filepath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        rel = str(filepath.relative_to(root))

        for pattern in patterns:
            for match in pattern.finditer(content):
                name = match.group("name")
                if name not in seen:
                    seen.add(name)
                    gd = match.groupdict()
                    has_default = "default" in gd and gd["default"] is not None
                    results.append(
                        EnvVar(name=name, source_file=rel, has_default=has_default)
                    )

    return sorted(results, key=lambda v: v.name)
