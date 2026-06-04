"""Tests for the project scanner."""

from pathlib import Path

import pytest

from preflight.scanner import SKIP_DIRS, scan_project

FIXTURES = Path(__file__).parent / "fixtures"


def test_scan_python_project():
    report = scan_project(FIXTURES / "python_project")
    assert report.path == str((FIXTURES / "python_project").resolve())

    lang_names = {lang.name for lang in report.languages}
    assert "Python" in lang_names

    pm_names = {pm.name for pm in report.package_managers}
    assert "pip" in pm_names

    env_names = {v.name for v in report.env_vars}
    assert "SECRET_KEY" in env_names


def test_scan_node_project():
    report = scan_project(FIXTURES / "node_project")

    lang_names = {lang.name for lang in report.languages}
    assert "JavaScript" in lang_names

    pm_names = {pm.name for pm in report.package_managers}
    assert "npm" in pm_names


def test_scan_docker_project():
    report = scan_project(FIXTURES / "docker_project")

    svc_names = {s.name for s in report.services}
    assert "web" in svc_names
    assert "postgres" in svc_names
    assert "redis" in svc_names


def test_scan_nonexistent_directory():
    with pytest.raises(NotADirectoryError):
        scan_project("/this/path/does/not/exist")


def test_scan_empty_directory(tmp_path):
    report = scan_project(tmp_path)
    assert report.languages == []
    assert report.package_managers == []
    assert report.env_vars == []
    assert report.services == []
    assert report.ports == []
    assert report.is_empty is True


def test_report_to_dict():
    report = scan_project(FIXTURES / "python_project")
    d = report.to_dict()
    assert "path" in d
    assert "summary" in d
    assert "languages" in d
    assert "package_managers" in d
    assert "env_vars" in d
    assert "services" in d
    assert "ports" in d
    assert isinstance(d["languages"], list)


def test_skip_dirs_includes_common_dirs():
    """Verify the skip list covers the most common noise directories."""
    assert ".git" in SKIP_DIRS
    assert "node_modules" in SKIP_DIRS
    assert "__pycache__" in SKIP_DIRS
    assert ".venv" in SKIP_DIRS
    assert "dist" in SKIP_DIRS
    assert "build" in SKIP_DIRS
    assert ".next" in SKIP_DIRS
    assert "target" in SKIP_DIRS


def test_scan_skips_node_modules(tmp_path):
    """Files inside node_modules should not appear in results."""
    src = tmp_path / "index.js"
    src.write_text("const PORT = 3000;\n")
    nm = tmp_path / "node_modules" / "express"
    nm.mkdir(parents=True)
    (nm / "index.js").write_text("module.exports = {};\n")
    report = scan_project(tmp_path)
    for lang in report.languages:
        if lang.name == "JavaScript":
            assert lang.file_count == 1  # only the root file


def test_scan_line_counts(tmp_path):
    py_file = tmp_path / "app.py"
    py_file.write_text("import os\nprint('hello')\n")
    report = scan_project(tmp_path)
    for lang in report.languages:
        if lang.name == "Python":
            assert lang.line_count > 0
