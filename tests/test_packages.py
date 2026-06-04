"""Tests for the package manager detector."""

from pathlib import Path

from preflight.detectors.packages import detect_packages

FIXTURES = Path(__file__).parent / "fixtures"


def test_detects_python_requirements():
    result = detect_packages(FIXTURES / "python_project")
    assert len(result) == 1
    pm = result[0]
    assert pm.name == "pip"
    assert pm.manifest_file == "requirements.txt"
    assert "flask" in pm.dependencies
    assert "requests" in pm.dependencies
    assert "gunicorn" in pm.dependencies
    assert "redis" in pm.dependencies


def test_detects_node_packages():
    result = detect_packages(FIXTURES / "node_project")
    assert len(result) == 1
    pm = result[0]
    assert pm.name == "npm"
    assert pm.manifest_file == "package.json"
    assert "express" in pm.dependencies
    assert "cors" in pm.dependencies
    assert "jest" in pm.dependencies


def test_no_manifests(tmp_path):
    result = detect_packages(tmp_path)
    assert result == []


def test_requirements_with_comments(tmp_path):
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("# this is a comment\nflask\n\n# another comment\nrequests>=2.0\n")
    result = detect_packages(tmp_path)
    assert len(result) == 1
    assert "flask" in result[0].dependencies
    assert "requests" in result[0].dependencies


def test_requirements_with_inline_comments(tmp_path):
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("flask>=2.0  # web framework\nredis  # cache\n")
    result = detect_packages(tmp_path)
    assert "flask" in result[0].dependencies
    assert "redis" in result[0].dependencies


def test_requirements_with_options(tmp_path):
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("-r base.txt\n--index-url https://pypi.org/simple\nflask\n")
    result = detect_packages(tmp_path)
    assert "flask" in result[0].dependencies
    assert len(result[0].dependencies) == 1  # option lines excluded


def test_go_mod_parsing(tmp_path):
    go_mod = tmp_path / "go.mod"
    go_mod.write_text(
        "module github.com/example/app\n\n"
        "go 1.21\n\n"
        "require (\n"
        "\tgithub.com/gin-gonic/gin v1.9.1\n"
        "\tgithub.com/lib/pq v1.10.9\n"
        ")\n"
    )
    result = detect_packages(tmp_path)
    assert len(result) == 1
    pm = result[0]
    assert pm.name == "go modules"
    assert "github.com/gin-gonic/gin" in pm.dependencies
    assert "github.com/lib/pq" in pm.dependencies


def test_go_mod_single_require(tmp_path):
    go_mod = tmp_path / "go.mod"
    go_mod.write_text(
        "module github.com/example/app\n\n"
        "go 1.21\n\n"
        "require github.com/gorilla/mux v1.8.0\n"
    )
    result = detect_packages(tmp_path)
    assert "github.com/gorilla/mux" in result[0].dependencies


def test_cargo_toml_parsing(tmp_path):
    cargo = tmp_path / "Cargo.toml"
    cargo.write_text(
        '[package]\nname = "myapp"\nversion = "0.1.0"\n\n'
        "[dependencies]\nserde = \"1.0\"\ntokio = { version = \"1\", features = [\"full\"] }\n\n"
        "[dev-dependencies]\ncriterion = \"0.5\"\n"
    )
    result = detect_packages(tmp_path)
    assert len(result) == 1
    pm = result[0]
    assert pm.name == "cargo"
    assert "serde" in pm.dependencies
    assert "tokio" in pm.dependencies
    assert "criterion" in pm.dependencies


def test_composer_json_parsing(tmp_path):
    composer = tmp_path / "composer.json"
    composer.write_text(
        '{"require": {"php": ">=8.1", "laravel/framework": "^10.0"}, '
        '"require-dev": {"phpunit/phpunit": "^10.0"}}'
    )
    result = detect_packages(tmp_path)
    assert len(result) == 1
    pm = result[0]
    assert pm.name == "composer"
    # php itself should be excluded
    assert "php" not in pm.dependencies
    assert "laravel/framework" in pm.dependencies
    assert "phpunit/phpunit" in pm.dependencies


def test_package_json_peer_dependencies(tmp_path):
    pkg = tmp_path / "package.json"
    pkg.write_text(
        '{"dependencies": {"react": "^18"}, '
        '"peerDependencies": {"react-dom": "^18"}}'
    )
    result = detect_packages(tmp_path)
    assert "react" in result[0].dependencies
    assert "react-dom" in result[0].dependencies


def test_does_not_duplicate_managers(tmp_path):
    """When both requirements.txt and pyproject.toml exist, only one pip entry appears."""
    (tmp_path / "requirements.txt").write_text("flask\n")
    (tmp_path / "pyproject.toml").write_text(
        "[project]\ndependencies = [\"click\"]\n"
    )
    result = detect_packages(tmp_path)
    pip_entries = [pm for pm in result if pm.name == "pip"]
    assert len(pip_entries) == 1
