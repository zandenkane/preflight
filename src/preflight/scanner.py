"""Project scanner that coordinates all detectors."""

from __future__ import annotations

from pathlib import Path

from preflight.detectors.envvars import detect_envvars
from preflight.detectors.languages import detect_languages
from preflight.detectors.packages import detect_packages
from preflight.detectors.ports import detect_ports
from preflight.detectors.services import detect_services
from preflight.models import ProjectReport

# Directories to skip during file tree traversal.
# These are build artifacts, caches, and dependency directories that would
# pollute scan results with irrelevant files.
SKIP_DIRS = {
    ".git",
    ".svn",
    ".hg",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "vendor",
    "dist",
    "build",
    "out",
    "target",
    ".tox",
    ".nox",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".eggs",
    ".egg-info",
    ".cache",
    ".next",
    ".nuxt",
    ".output",
    ".parcel-cache",
    "coverage",
    "htmlcov",
    ".terraform",
}


def _collect_files(root: Path, max_depth: int = 20) -> list[Path]:
    """Walk the directory tree, skipping ignored directories.

    Args:
        root: The starting directory.
        max_depth: Maximum recursion depth to prevent runaway scans.

    Returns a list of file paths.
    """
    files: list[Path] = []

    def _walk(directory: Path, depth: int) -> None:
        if depth > max_depth:
            return

        try:
            entries = sorted(directory.iterdir())
        except PermissionError:
            return

        for entry in entries:
            if entry.is_dir():
                if entry.name not in SKIP_DIRS:
                    _walk(entry, depth + 1)
            elif entry.is_file():
                files.append(entry)

    _walk(root, 0)
    return files


def scan_project(path: str | Path) -> ProjectReport:
    """Scan a project directory and return a full report.

    Walks the directory tree, runs all detectors, and collects results
    into a ProjectReport.

    Raises NotADirectoryError if the path does not exist or is not a directory.
    """
    root = Path(path).resolve()

    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root}")

    files = _collect_files(root)

    # Run detectors
    languages = detect_languages(files)
    package_managers = detect_packages(root)
    env_vars = detect_envvars(root, files)
    services = detect_services(root)

    # Build compose service dicts for port detector
    compose_svc_dicts = []
    for svc in services:
        if svc.source == "docker-compose":
            compose_svc_dicts.append({"ports": svc.ports})

    ports = detect_ports(root, files, compose_services=compose_svc_dicts)

    return ProjectReport(
        path=str(root),
        languages=languages,
        package_managers=package_managers,
        env_vars=env_vars,
        services=services,
        ports=ports,
    )
