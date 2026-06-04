"""Tests for the service detector."""

from pathlib import Path

from preflight.detectors.services import detect_services

FIXTURES = Path(__file__).parent / "fixtures"


def test_detects_docker_compose_services():
    result = detect_services(FIXTURES / "docker_project")
    compose_services = [s for s in result if s.source == "docker-compose"]
    names = {s.name for s in compose_services}
    assert "web" in names
    assert "postgres" in names
    assert "redis" in names


def test_docker_compose_images():
    result = detect_services(FIXTURES / "docker_project")
    by_name = {s.name: s for s in result if s.source == "docker-compose"}
    assert by_name["postgres"].image == "postgres:15"
    assert by_name["redis"].image == "redis:7-alpine"


def test_docker_compose_ports():
    result = detect_services(FIXTURES / "docker_project")
    by_name = {s.name: s for s in result if s.source == "docker-compose"}
    assert "5432:5432" in by_name["postgres"].ports
    assert "6379:6379" in by_name["redis"].ports


def test_detects_dockerfile():
    result = detect_services(FIXTURES / "docker_project")
    dockerfile_services = [s for s in result if s.source == "Dockerfile"]
    assert len(dockerfile_services) == 1
    assert "8000" in dockerfile_services[0].ports


def test_no_services(tmp_path):
    result = detect_services(tmp_path)
    assert result == []


def test_detects_procfile(tmp_path):
    procfile = tmp_path / "Procfile"
    procfile.write_text("web: gunicorn app:app\nworker: celery -A tasks worker\n")
    result = detect_services(tmp_path)
    names = {s.name for s in result}
    assert "web" in names
    assert "worker" in names
    for svc in result:
        assert svc.source == "Procfile"


def test_procfile_ignores_comments(tmp_path):
    procfile = tmp_path / "Procfile"
    procfile.write_text("# this is a comment\nweb: python app.py\n\n")
    result = detect_services(tmp_path)
    assert len(result) == 1
    assert result[0].name == "web"


def test_compose_yml_alternative_name(tmp_path):
    compose = tmp_path / "compose.yml"
    compose.write_text(
        "services:\n  api:\n    image: node:18\n    ports:\n      - '3000:3000'\n"
    )
    result = detect_services(tmp_path)
    names = {s.name for s in result}
    assert "api" in names


def test_dockerfile_multiple_expose(tmp_path):
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM python:3.12\nEXPOSE 8000\nEXPOSE 8443\n")
    result = detect_services(tmp_path)
    dockerfile_svcs = [s for s in result if s.source == "Dockerfile"]
    assert len(dockerfile_svcs) == 1
    assert "8000" in dockerfile_svcs[0].ports
    assert "8443" in dockerfile_svcs[0].ports


def test_compose_with_build_and_no_image(tmp_path):
    compose = tmp_path / "docker-compose.yml"
    compose.write_text("services:\n  app:\n    build: .\n    ports:\n      - '8080:8080'\n")
    result = detect_services(tmp_path)
    app = [s for s in result if s.name == "app"]
    assert len(app) == 1
    assert app[0].image == ""
    assert "8080:8080" in app[0].ports
