"""Tests for the language detector."""

from pathlib import Path

from preflight.detectors.languages import EXTENSION_MAP, detect_languages


def test_detects_python_files():
    files = [
        Path("app.py"),
        Path("utils.py"),
        Path("test_app.py"),
    ]
    result = detect_languages(files, count_lines=False)
    assert len(result) == 1
    assert result[0].name == "Python"
    assert result[0].file_count == 3


def test_detects_multiple_languages():
    files = [
        Path("app.py"),
        Path("index.js"),
        Path("style.css"),  # not in the map
        Path("main.go"),
    ]
    result = detect_languages(files, count_lines=False)
    names = {lang.name for lang in result}
    assert "Python" in names
    assert "JavaScript" in names
    assert "Go" in names
    assert len(result) == 3  # CSS not detected


def test_sorts_by_file_count():
    files = [
        Path("a.js"),
        Path("b.js"),
        Path("c.js"),
        Path("app.py"),
    ]
    result = detect_languages(files, count_lines=False)
    assert result[0].name == "JavaScript"
    assert result[0].file_count == 3
    assert result[1].name == "Python"
    assert result[1].file_count == 1


def test_handles_typescript():
    files = [
        Path("app.ts"),
        Path("component.tsx"),
    ]
    result = detect_languages(files, count_lines=False)
    assert len(result) == 1
    assert result[0].name == "TypeScript"
    assert result[0].file_count == 2


def test_empty_file_list():
    result = detect_languages([])
    assert result == []


def test_no_recognized_extensions():
    files = [
        Path("README.md"),
        Path("config.yml"),
        Path("data.csv"),
    ]
    result = detect_languages(files, count_lines=False)
    assert result == []


def test_counts_lines(tmp_path):
    py_file = tmp_path / "app.py"
    py_file.write_text("import os\n\ndef main():\n    pass\n\n")
    result = detect_languages([py_file], count_lines=True)
    assert result[0].line_count == 3  # blank lines excluded


def test_handles_mjs_cjs():
    files = [Path("module.mjs"), Path("compat.cjs")]
    result = detect_languages(files, count_lines=False)
    assert len(result) == 1
    assert result[0].name == "JavaScript"
    assert result[0].file_count == 2


def test_kotlin_and_swift_detection():
    files = [Path("Main.kt"), Path("App.swift")]
    result = detect_languages(files, count_lines=False)
    names = {lang.name for lang in result}
    assert "Kotlin" in names
    assert "Swift" in names


def test_shell_scripts():
    files = [Path("setup.sh"), Path("deploy.bash"), Path("init.zsh")]
    result = detect_languages(files, count_lines=False)
    assert len(result) == 1
    assert result[0].name == "Shell"
    assert result[0].file_count == 3


def test_extension_map_completeness():
    """Verify all mapped extensions produce a non-empty language name."""
    for ext, lang in EXTENSION_MAP.items():
        assert ext.startswith(".")
        assert len(lang) > 0


def test_rust_detection():
    files = [Path("main.rs"), Path("lib.rs")]
    result = detect_languages(files, count_lines=False)
    assert len(result) == 1
    assert result[0].name == "Rust"
    assert result[0].file_count == 2
