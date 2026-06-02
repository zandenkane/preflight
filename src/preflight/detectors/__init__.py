"""Detectors for languages, packages, env vars, services, and ports."""

from preflight.detectors.envvars import detect_envvars
from preflight.detectors.languages import detect_languages
from preflight.detectors.packages import detect_packages
from preflight.detectors.ports import detect_ports
from preflight.detectors.services import detect_services

__all__ = [
    "detect_envvars",
    "detect_languages",
    "detect_packages",
    "detect_ports",
    "detect_services",
]
