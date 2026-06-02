"""Detect port bindings from source code, Dockerfiles, and compose files."""

from __future__ import annotations

import re
from pathlib import Path

from preflight.models import Port

# Well-known port labels
KNOWN_PORTS: dict[int, str] = {
    22: "SSH",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    443: "HTTPS",
    1433: "MSSQL",
    1521: "Oracle DB",
    2181: "ZooKeeper",
    3000: "Node.js dev server",
    3306: "MySQL",
    4200: "Angular dev server",
    4443: "HTTPS alt",
    5000: "Flask dev server",
    5173: "Vite dev server",
    5432: "PostgreSQL",
    5672: "RabbitMQ",
    5900: "VNC",
    6379: "Redis",
    6380: "Redis TLS",
    8000: "Python dev server",
    8080: "HTTP alt",
    8443: "HTTPS alt",
    8500: "Consul",
    8888: "Jupyter",
    9000: "SonarQube",
    9090: "Prometheus",
    9092: "Kafka",
    9200: "Elasticsearch",
    9300: "Elasticsearch transport",
    11211: "Memcached",
    15672: "RabbitMQ management",
    27017: "MongoDB",
    28017: "MongoDB HTTP",
}

# Regex patterns to find port bindings in source code
SOURCE_PORT_PATTERNS = [
    # .listen(PORT) or .listen(3000)
    re.compile(r"""\.listen\(\s*(\d{2,5})\s*[,)]"""),
    # bind("0.0.0.0", PORT) or bind("host", PORT)
    re.compile(r"""\.bind\(\s*["'][^"']*["']\s*,\s*(\d{2,5})\s*\)"""),
    # PORT = 8000 or port = 3000 (variable assignment)
    re.compile(r"""(?i)\bport\s*=\s*(\d{2,5})\b"""),
    # :port => 3000 (Ruby)
    re.compile(r""":port\s*=>\s*(\d{2,5})"""),
    # uvicorn ... --port 8000
    re.compile(r"""--port\s+(\d{2,5})"""),
    # Addr(":8080") or ListenAndServe(":8080" (Go)
    re.compile(r"""["']:(\d{2,5})["']"""),
]

# Dockerfile EXPOSE pattern
EXPOSE_PATTERN = re.compile(r"^EXPOSE\s+(.+)$", re.MULTILINE)

SOURCE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".mjs", ".cjs",
    ".go", ".rs", ".rb", ".java", ".php", ".kt", ".scala",
}


def _label_port(port_num: int) -> str:
    return KNOWN_PORTS.get(port_num, "")


def _extract_ports_from_source(filepath: Path, root: Path) -> list[Port]:
    try:
        content = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    rel = str(filepath.relative_to(root))
    results = []

    for pattern in SOURCE_PORT_PATTERNS:
        for match in pattern.finditer(content):
            try:
                port_num = int(match.group(1))
            except (ValueError, IndexError):
                continue
            if 1 <= port_num <= 65535:
                results.append(
                    Port(
                        number=port_num,
                        label=_label_port(port_num),
                        source=rel,
                    )
                )

    return results


def _extract_ports_from_dockerfile(path: Path) -> list[Port]:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    results = []
    for match in EXPOSE_PATTERN.finditer(content):
        raw = match.group(1).strip()
        for part in raw.split():
            port_str = part.split("/")[0]
            try:
                port_num = int(port_str)
                results.append(
                    Port(
                        number=port_num,
                        label=_label_port(port_num),
                        source="Dockerfile",
                    )
                )
            except ValueError:
                continue

    return results


def _extract_ports_from_compose(services: list[dict]) -> list[Port]:
    results = []
    for svc in services:
        for port_str in svc.get("ports", []):
            # Format: "host:container" or just "container"
            parts = str(port_str).split(":")
            try:
                port_num = int(parts[-1].split("/")[0])
                results.append(
                    Port(
                        number=port_num,
                        label=_label_port(port_num),
                        source="docker-compose",
                    )
                )
            except ValueError:
                continue
            # Also add host port if different
            if len(parts) >= 2:
                try:
                    host_port = int(parts[0].split("/")[0])
                    if host_port != port_num:
                        results.append(
                            Port(
                                number=host_port,
                                label=_label_port(host_port),
                                source="docker-compose",
                            )
                        )
                except ValueError:
                    continue

    return results


def detect_ports(
    root: Path,
    files: list[Path],
    compose_services: list[dict] | None = None,
) -> list[Port]:
    """Scan for port bindings across source files, Dockerfiles, and compose config.

    Returns a deduplicated list of ports sorted by port number.
    """
    all_ports: list[Port] = []

    # Source files
    for filepath in files:
        if filepath.suffix.lower() in SOURCE_EXTENSIONS:
            all_ports.extend(_extract_ports_from_source(filepath, root))

    # Dockerfile
    dockerfile_path = root / "Dockerfile"
    if dockerfile_path.is_file():
        all_ports.extend(_extract_ports_from_dockerfile(dockerfile_path))

    # Docker Compose services
    if compose_services:
        all_ports.extend(_extract_ports_from_compose(compose_services))

    # Deduplicate by port number
    seen: set[int] = set()
    unique: list[Port] = []
    for port in all_ports:
        if port.number not in seen:
            seen.add(port.number)
            unique.append(port)

    return sorted(unique, key=lambda p: p.number)
