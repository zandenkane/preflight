"""Shared test fixtures and configuration."""

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the path to the test fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture
def python_project(fixtures_dir: Path) -> Path:
    """Return the path to the Python fixture project."""
    return fixtures_dir / "python_project"


@pytest.fixture
def node_project(fixtures_dir: Path) -> Path:
    """Return the path to the Node fixture project."""
    return fixtures_dir / "node_project"


@pytest.fixture
def docker_project(fixtures_dir: Path) -> Path:
    """Return the path to the Docker fixture project."""
    return fixtures_dir / "docker_project"
