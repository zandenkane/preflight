"""Tests for the output formatters."""

import json

from preflight.formatters.terminal import render_json, render_terminal
from preflight.models import (
    EnvVar,
    Language,
    PackageManager,
    Port,
    ProjectReport,
    Service,
)


def _sample_report() -> ProjectReport:
    return ProjectReport(
        path="/tmp/sample",
        languages=[
            Language(name="Python", extension=".py", file_count=10, line_count=500),
            Language(name="JavaScript", extension=".js", file_count=5, line_count=200),
        ],
        package_managers=[
            PackageManager(
                name="pip",
                manifest_file="requirements.txt",
                dependencies=["flask", "redis"],
            ),
        ],
        env_vars=[
            EnvVar(name="SECRET_KEY", source_file="app.py", has_default=False),
            EnvVar(name="DEBUG", source_file="app.py", has_default=True),
        ],
        services=[
            Service(name="web", image="", ports=["8080:8000"], source="docker-compose"),
        ],
        ports=[
            Port(number=5432, label="PostgreSQL", source="docker-compose"),
        ],
    )


def test_render_json_valid():
    report = _sample_report()
    output = render_json(report)
    data = json.loads(output)
    assert data["path"] == "/tmp/sample"
    assert len(data["languages"]) == 2
    assert data["summary"]["languages_found"] == 2


def test_render_json_empty_report():
    report = ProjectReport(path="/tmp/empty")
    output = render_json(report)
    data = json.loads(output)
    assert data["languages"] == []
    assert data["summary"]["languages_found"] == 0


def test_render_terminal_no_crash():
    """Verify terminal rendering completes without raising exceptions."""
    report = _sample_report()
    render_terminal(report, no_color=True)


def test_render_terminal_empty_report():
    """Verify empty report rendering does not crash."""
    report = ProjectReport(path="/tmp/empty")
    render_terminal(report, no_color=True)


def test_render_json_preserves_all_fields():
    report = _sample_report()
    data = json.loads(render_json(report))
    # Check all top-level keys exist
    expected_keys = (
        "path", "summary", "languages",
        "package_managers", "env_vars", "services", "ports",
    )
    for key in expected_keys:
        assert key in data


def test_render_json_envvar_required_field():
    report = _sample_report()
    data = json.loads(render_json(report))
    for ev in data["env_vars"]:
        assert "required" in ev
    secret = [ev for ev in data["env_vars"] if ev["name"] == "SECRET_KEY"][0]
    assert secret["required"] is True
    debug = [ev for ev in data["env_vars"] if ev["name"] == "DEBUG"][0]
    assert debug["required"] is False


def test_render_json_language_line_count():
    report = _sample_report()
    data = json.loads(render_json(report))
    python = [x for x in data["languages"] if x["name"] == "Python"][0]
    assert python["line_count"] == 500
