"""Detect services from Docker Compose, Dockerfile, and Procfile."""

from __future__ import annotations

import re
from pathlib import Path

from preflight.models import Service

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

# All supported compose file names, checked in priority order
COMPOSE_FILENAMES = (
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
)


def _parse_docker_compose(path: Path) -> list[Service]:
    if yaml is None:
        return []

    try:
        content = path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
    except (OSError, Exception):
        return []

    if not isinstance(data, dict):
        return []

    services_section = data.get("services", {})
    if not isinstance(services_section, dict):
        return []

    results = []
    for svc_name, svc_config in services_section.items():
        if not isinstance(svc_config, dict):
            continue

        image = svc_config.get("image", "")
        ports_raw = svc_config.get("ports", [])
        ports = [str(p) for p in ports_raw] if isinstance(ports_raw, list) else []

        results.append(
            Service(
                name=svc_name,
                image=image or "",
                ports=ports,
                source="docker-compose",
            )
        )

    return results


def _parse_dockerfile(path: Path) -> list[Service]:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    expose_pattern = re.compile(r"^EXPOSE\s+(.+)$", re.MULTILINE)
    ports = []
    for match in expose_pattern.finditer(content):
        raw = match.group(1).strip()
        for part in raw.split():
            port_str = part.split("/")[0]  # strip /tcp, /udp
            ports.append(port_str)

    return [
        Service(
            name="Dockerfile",
            image="",
            ports=ports,
            source="Dockerfile",
        )
    ]


def _parse_procfile(path: Path) -> list[Service]:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    results = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            name = line.split(":")[0].strip()
            results.append(
                Service(name=name, image="", ports=[], source="Procfile")
            )

    return results


def detect_services(root: Path) -> list[Service]:
    """Scan the project root for Docker Compose, Dockerfile, and Procfile.

    Checks multiple compose file names (docker-compose.yml, compose.yml, etc.)
    and stops at the first one found.
    """
    results: list[Service] = []

    # Docker Compose (try multiple filenames)
    for compose_name in COMPOSE_FILENAMES:
        compose_path = root / compose_name
        if compose_path.is_file():
            results.extend(_parse_docker_compose(compose_path))
            break

    # Dockerfile
    dockerfile_path = root / "Dockerfile"
    if dockerfile_path.is_file():
        results.extend(_parse_dockerfile(dockerfile_path))

    # Procfile
    procfile_path = root / "Procfile"
    if procfile_path.is_file():
        results.extend(_parse_procfile(procfile_path))

    return results
