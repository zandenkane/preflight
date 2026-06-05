"""Detect package managers and parse dependencies from manifest files."""

from __future__ import annotations

import json
import re
from pathlib import Path

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        tomllib = None  # type: ignore[assignment]

from preflight.models import PackageManager

# Maps manifest filename to package manager name.
# Order matters: the first matching manifest for a given manager wins.
MANIFEST_MAP: dict[str, str] = {
    "requirements.txt": "pip",
    "pyproject.toml": "pip",
    "setup.py": "pip",
    "setup.cfg": "pip",
    "Pipfile": "pipenv",
    "Pipfile.lock": "pipenv",
    "poetry.lock": "poetry",
    "package.json": "npm",
    "yarn.lock": "yarn",
    "pnpm-lock.yaml": "pnpm",
    "bun.lockb": "bun",
    "go.mod": "go modules",
    "Cargo.toml": "cargo",
    "Gemfile": "bundler",
    "composer.json": "composer",
    "pom.xml": "maven",
    "build.gradle": "gradle",
    "build.gradle.kts": "gradle",
    "mix.exs": "mix",
    "Package.swift": "swift package manager",
    "pubspec.yaml": "pub",
}


def _parse_requirements_txt(path: Path) -> list[str]:
    """Extract package names from requirements.txt.

    Handles comments, blank lines, option flags, and inline comments.
    Strips version specifiers and extras brackets.
    """
    deps = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            # Remove inline comments
            if " #" in line:
                line = line[: line.index(" #")]
            # Strip version specifiers, extras, and environment markers
            name = re.split(r"[>=<!;\[\]@\s]", line)[0].strip()
            if name:
                deps.append(name)
    except (OSError, UnicodeDecodeError):
        pass
    return deps


def _parse_pyproject_toml(path: Path) -> list[str]:
    if tomllib is None:
        return []
    deps = []
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        raw_deps = data.get("project", {}).get("dependencies", [])
        for dep in raw_deps:
            name = re.split(r"[>=<!;\[\]@\s]", dep)[0].strip()
            if name:
                deps.append(name)
    except (OSError, UnicodeDecodeError, Exception):
        pass
    return deps


def _parse_package_json(path: Path) -> list[str]:
    """Extract dependency names from package.json.

    Reads both dependencies and devDependencies sections.
    """
    deps = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        for key in ("dependencies", "devDependencies", "peerDependencies"):
            section = data.get(key, {})
            if isinstance(section, dict):
                deps.extend(section.keys())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        pass
    return deps


def _parse_go_mod(path: Path) -> list[str]:
    deps = []
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return deps

    in_require_block = False
    for line in content.splitlines():
        stripped = line.strip()

        if stripped.startswith("require ("):
            in_require_block = True
            continue
        if in_require_block and stripped == ")":
            in_require_block = False
            continue

        if in_require_block:
            # Lines like: github.com/foo/bar v1.2.3
            parts = stripped.split()
            if parts and not parts[0].startswith("//"):
                deps.append(parts[0])
        elif stripped.startswith("require ") and "(" not in stripped:
            # Single-line require: require github.com/foo/bar v1.2.3
            parts = stripped.split()
            if len(parts) >= 2:
                deps.append(parts[1])

    return deps


def _parse_cargo_toml(path: Path) -> list[str]:
    if tomllib is None:
        return []
    deps = []
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        for section_key in ("dependencies", "dev-dependencies", "build-dependencies"):
            section = data.get(section_key, {})
            if isinstance(section, dict):
                deps.extend(section.keys())
    except (OSError, UnicodeDecodeError, Exception):
        pass
    return deps


def _parse_composer_json(path: Path) -> list[str]:
    deps = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        for key in ("require", "require-dev"):
            section = data.get(key, {})
            if isinstance(section, dict):
                for pkg_name in section.keys():
                    # Skip php itself and extensions
                    if pkg_name == "php" or pkg_name.startswith("ext-"):
                        continue
                    deps.append(pkg_name)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        pass
    return deps


def detect_packages(root: Path) -> list[PackageManager]:
    """Scan the root directory for manifest files and parse dependencies.

    For supported ecosystems (Python, Node, Go, Rust, PHP), actual dependency
    names are extracted. For other ecosystems, the package manager is detected
    but deps are not parsed.
    """
    results: list[PackageManager] = []
    seen_managers: set[str] = set()

    for manifest_name, manager_name in MANIFEST_MAP.items():
        manifest_path = root / manifest_name
        if not manifest_path.is_file():
            continue

        # Skip duplicates for the same manager
        if manager_name in seen_managers:
            continue
        seen_managers.add(manager_name)

        deps: list[str] = []

        if manifest_name == "requirements.txt":
            deps = _parse_requirements_txt(manifest_path)
        elif manifest_name == "pyproject.toml":
            deps = _parse_pyproject_toml(manifest_path)
        elif manifest_name == "package.json":
            deps = _parse_package_json(manifest_path)
        elif manifest_name == "go.mod":
            deps = _parse_go_mod(manifest_path)
        elif manifest_name == "Cargo.toml":
            deps = _parse_cargo_toml(manifest_path)
        elif manifest_name == "composer.json":
            deps = _parse_composer_json(manifest_path)

        results.append(
            PackageManager(
                name=manager_name,
                manifest_file=manifest_name,
                dependencies=deps,
            )
        )

    return results
