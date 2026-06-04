"""Tests for the CLI entry point."""

import json
from pathlib import Path

from click.testing import CliRunner

from preflight.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


def test_cli_default_runs():
    runner = CliRunner()
    result = runner.invoke(main, [str(FIXTURES / "python_project")])
    assert result.exit_code == 0
    assert "Python" in result.output


def test_cli_json_output():
    runner = CliRunner()
    result = runner.invoke(main, [str(FIXTURES / "python_project"), "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "languages" in data
    assert "package_managers" in data
    assert "env_vars" in data
    assert "summary" in data


def test_cli_no_color():
    runner = CliRunner()
    result = runner.invoke(main, [str(FIXTURES / "python_project"), "--no-color"])
    assert result.exit_code == 0


def test_cli_nonexistent_path():
    runner = CliRunner()
    result = runner.invoke(main, ["/nonexistent/path/here"])
    assert result.exit_code != 0


def test_cli_node_project():
    runner = CliRunner()
    result = runner.invoke(main, [str(FIXTURES / "node_project"), "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    lang_names = {lang["name"] for lang in data["languages"]}
    assert "JavaScript" in lang_names


def test_cli_docker_project():
    runner = CliRunner()
    result = runner.invoke(main, [str(FIXTURES / "docker_project"), "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    svc_names = {s["name"] for s in data["services"]}
    assert "postgres" in svc_names


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "preflight" in result.output
    assert "0.1.0" in result.output


def test_cli_quiet_mode():
    runner = CliRunner()
    result = runner.invoke(main, [str(FIXTURES / "python_project"), "--quiet"])
    assert result.exit_code == 0
    assert "languages:" in result.output


def test_cli_quiet_empty_project(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "--quiet"])
    assert result.exit_code == 0
    assert "No project configuration detected." in result.output


def test_cli_json_includes_line_counts():
    runner = CliRunner()
    result = runner.invoke(main, [str(FIXTURES / "python_project"), "--json"])
    data = json.loads(result.output)
    for lang in data["languages"]:
        assert "line_count" in lang


def test_cli_json_envvar_has_required_field():
    runner = CliRunner()
    result = runner.invoke(main, [str(FIXTURES / "python_project"), "--json"])
    data = json.loads(result.output)
    for ev in data["env_vars"]:
        assert "required" in ev
