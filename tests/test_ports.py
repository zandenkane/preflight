"""Tests for the port detector."""

from pathlib import Path

from preflight.detectors.ports import KNOWN_PORTS, detect_ports

FIXTURES = Path(__file__).parent / "fixtures"


def test_detects_ports_from_python_source():
    root = FIXTURES / "python_project"
    files = list(root.rglob("*.py"))
    result = detect_ports(root, files)
    port_numbers = {p.number for p in result}
    assert 5000 in port_numbers


def test_detects_ports_from_js_source():
    root = FIXTURES / "node_project"
    files = list(root.rglob("*.js"))
    result = detect_ports(root, files)
    port_numbers = {p.number for p in result}
    assert 3000 in port_numbers


def test_detects_dockerfile_expose():
    root = FIXTURES / "docker_project"
    result = detect_ports(root, [])
    port_numbers = {p.number for p in result}
    assert 8000 in port_numbers


def test_detects_compose_ports():
    compose_services = [
        {"ports": ["5432:5432"]},
        {"ports": ["6379:6379"]},
    ]
    result = detect_ports(FIXTURES / "docker_project", [], compose_services=compose_services)
    port_numbers = {p.number for p in result}
    assert 5432 in port_numbers
    assert 6379 in port_numbers


def test_labels_known_ports():
    assert KNOWN_PORTS[5432] == "PostgreSQL"
    assert KNOWN_PORTS[6379] == "Redis"
    assert KNOWN_PORTS[3306] == "MySQL"
    assert KNOWN_PORTS[27017] == "MongoDB"
    assert KNOWN_PORTS[22] == "SSH"
    assert KNOWN_PORTS[9092] == "Kafka"


def test_deduplicates_ports():
    compose_services = [
        {"ports": ["5432:5432"]},
        {"ports": ["5432:5432"]},
    ]
    result = detect_ports(FIXTURES / "docker_project", [], compose_services=compose_services)
    port_5432 = [p for p in result if p.number == 5432]
    assert len(port_5432) == 1


def test_sorted_by_port_number():
    compose_services = [
        {"ports": ["6379:6379"]},
        {"ports": ["3306:3306"]},
        {"ports": ["5432:5432"]},
    ]
    result = detect_ports(Path("."), [], compose_services=compose_services)
    numbers = [p.number for p in result]
    assert numbers == sorted(numbers)


def test_empty_project(tmp_path):
    result = detect_ports(tmp_path, [])
    assert result == []


def test_host_and_container_ports_differ():
    """When host and container ports differ, both should be recorded."""
    compose_services = [{"ports": ["8080:3000"]}]
    result = detect_ports(Path("."), [], compose_services=compose_services)
    port_numbers = {p.number for p in result}
    assert 3000 in port_numbers
    assert 8080 in port_numbers


def test_port_from_source_has_label(tmp_path):
    py_file = tmp_path / "app.py"
    py_file.write_text("app.listen(5432)\n")
    result = detect_ports(tmp_path, [py_file])
    pg = [p for p in result if p.number == 5432]
    assert len(pg) == 1
    assert pg[0].label == "PostgreSQL"


def test_port_variable_assignment_detection(tmp_path):
    py_file = tmp_path / "config.py"
    py_file.write_text("PORT = 9090\nDEBUG = True\n")
    result = detect_ports(tmp_path, [py_file])
    port_numbers = {p.number for p in result}
    assert 9090 in port_numbers


def test_dockerfile_expose_with_protocol(tmp_path):
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM python:3.11\nEXPOSE 8080/tcp 9090/udp\n")
    result = detect_ports(tmp_path, [])
    port_numbers = {p.number for p in result}
    assert 8080 in port_numbers
    assert 9090 in port_numbers


def test_multiple_expose_lines(tmp_path):
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM node:18\nEXPOSE 3000\nEXPOSE 8080\n")
    result = detect_ports(tmp_path, [])
    port_numbers = {p.number for p in result}
    assert 3000 in port_numbers
    assert 8080 in port_numbers
