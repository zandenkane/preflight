"""Detect programming languages by file extension and count lines of code."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from preflight.models import Language

EXTENSION_MAP: dict[str, str] = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".jsx": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".c": "C",
    ".cpp": "C++",
    ".cc": "C++",
    ".h": "C",
    ".hpp": "C++",
    ".swift": "Swift",
    ".scala": "Scala",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".lua": "Lua",
    ".r": "R",
    ".R": "R",
    ".dart": "Dart",
    ".ex": "Elixir",
    ".exs": "Elixir",
    ".erl": "Erlang",
    ".zig": "Zig",
    ".nim": "Nim",
    ".pl": "Perl",
    ".pm": "Perl",
}


def _count_lines(path: Path) -> int:
    """Count the number of non-blank lines in a file.

    Returns 0 if the file cannot be read.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        return sum(1 for line in text.splitlines() if line.strip())
    except OSError:
        return 0


def detect_languages(files: list[Path], count_lines: bool = True) -> list[Language]:
    """Count files per language based on extension mapping.

    When count_lines is True, each file is opened to count non-blank lines.
    Returns languages sorted by file count, descending.
    """
    file_counts: Counter[str] = Counter()
    line_counts: Counter[str] = Counter()
    ext_for_lang: dict[str, str] = {}

    for path in files:
        ext = path.suffix.lower()
        lang_name = EXTENSION_MAP.get(ext)
        if lang_name:
            file_counts[lang_name] += 1
            if lang_name not in ext_for_lang:
                ext_for_lang[lang_name] = ext
            if count_lines:
                line_counts[lang_name] += _count_lines(path)

    results = []
    for lang_name, count in file_counts.most_common():
        results.append(
            Language(
                name=lang_name,
                extension=ext_for_lang[lang_name],
                file_count=count,
                line_count=line_counts.get(lang_name, 0),
            )
        )

    return results
