"""Tests for the environment variable detector."""

from pathlib import Path

from preflight.detectors.envvars import detect_envvars

FIXTURES = Path(__file__).parent / "fixtures"


def test_detects_python_envvars():
    root = FIXTURES / "python_project"
    files = list(root.rglob("*.py"))
    result = detect_envvars(root, files)
    names = {v.name for v in result}
    assert "SECRET_KEY" in names
    assert "DATABASE_URL" in names
    assert "DEBUG" in names
    assert "PORT" in names


def test_python_default_detection():
    root = FIXTURES / "python_project"
    files = list(root.rglob("*.py"))
    result = detect_envvars(root, files)
    by_name = {v.name: v for v in result}

    # DATABASE_URL has a default ("sqlite:///db.sqlite3")
    assert by_name["DATABASE_URL"].has_default is True
    # SECRET_KEY is os.environ["SECRET_KEY"], no default
    assert by_name["SECRET_KEY"].has_default is False


def test_detects_node_envvars():
    root = FIXTURES / "node_project"
    files = list(root.rglob("*.js"))
    result = detect_envvars(root, files)
    names = {v.name for v in result}
    assert "PORT" in names
    assert "API_KEY" in names
    assert "NODE_ENV" in names


def test_empty_project(tmp_path):
    result = detect_envvars(tmp_path, [])
    assert result == []


def test_dotenv_parsing(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DATABASE_URL=postgres://localhost/db\nSECRET_KEY=\nDEBUG=true\n")
    result = detect_envvars(tmp_path, [])
    names = {v.name for v in result}
    assert "DATABASE_URL" in names
    assert "SECRET_KEY" in names
    assert "DEBUG" in names

    by_name = {v.name: v for v in result}
    assert by_name["DATABASE_URL"].has_default is True
    assert by_name["SECRET_KEY"].has_default is False  # empty value


def test_dotenv_example_parsing(tmp_path):
    env_file = tmp_path / ".env.example"
    env_file.write_text("API_KEY=\nSECRET=change_me\n")
    result = detect_envvars(tmp_path, [])
    names = {v.name for v in result}
    assert "API_KEY" in names
    assert "SECRET" in names


def test_deduplicates_across_files(tmp_path):
    """Variables found in .env should not be duplicated from source files."""
    env_file = tmp_path / ".env"
    env_file.write_text("PORT=3000\n")
    py_file = tmp_path / "app.py"
    py_file.write_text('import os\nport = os.getenv("PORT", "3000")\n')
    result = detect_envvars(tmp_path, [py_file])
    port_entries = [v for v in result if v.name == "PORT"]
    assert len(port_entries) == 1


def test_results_sorted_alphabetically(tmp_path):
    py_file = tmp_path / "app.py"
    py_file.write_text(
        'import os\n'
        'z = os.getenv("ZEBRA")\n'
        'a = os.getenv("APPLE")\n'
        'm = os.getenv("MANGO")\n'
    )
    result = detect_envvars(tmp_path, [py_file])
    names = [v.name for v in result]
    assert names == sorted(names)


def test_go_envvar_detection(tmp_path):
    go_file = tmp_path / "main.go"
    go_file.write_text('package main\nimport "os"\nvar key = os.Getenv("API_KEY")\n')
    result = detect_envvars(tmp_path, [go_file])
    names = {v.name for v in result}
    assert "API_KEY" in names


def test_ruby_envvar_detection(tmp_path):
    rb_file = tmp_path / "app.rb"
    rb_file.write_text('db = ENV["DATABASE_URL"]\nsecret = ENV.fetch("SECRET", "default")\n')
    result = detect_envvars(tmp_path, [rb_file])
    names = {v.name for v in result}
    assert "DATABASE_URL" in names
    assert "SECRET" in names
    by_name = {v.name: v for v in result}
    assert by_name["SECRET"].has_default is True


def test_rust_envvar_detection(tmp_path):
    rs_file = tmp_path / "main.rs"
    rs_file.write_text('use std::env;\nlet key = env::var("DATABASE_URL").unwrap();\n')
    result = detect_envvars(tmp_path, [rs_file])
    names = {v.name for v in result}
    assert "DATABASE_URL" in names


def test_php_envvar_detection(tmp_path):
    php_file = tmp_path / "index.php"
    php_file.write_text('<?php\n$key = getenv("APP_KEY");\n$db = $_ENV["DB_HOST"];\n')
    result = detect_envvars(tmp_path, [php_file])
    names = {v.name for v in result}
    assert "APP_KEY" in names
    assert "DB_HOST" in names
