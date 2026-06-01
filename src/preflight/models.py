"""Data containers for project scanning results."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Language:

    name: str
    extension: str
    file_count: int = 0
    line_count: int = 0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "extension": self.extension,
            "file_count": self.file_count,
            "line_count": self.line_count,
        }


@dataclass
class PackageManager:

    name: str
    manifest_file: str
    dependencies: list[str] = field(default_factory=list)

    @property
    def dependency_count(self) -> int:
        """Return the number of parsed dependencies."""
        return len(self.dependencies)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "manifest_file": self.manifest_file,
            "dependencies": self.dependencies,
            "dependency_count": self.dependency_count,
        }


@dataclass
class EnvVar:
    """An environment variable reference found in source code."""

    name: str
    source_file: str
    has_default: bool = False

    @property
    def required(self) -> bool:
        return not self.has_default

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "source_file": self.source_file,
            "has_default": self.has_default,
            "required": self.required,
        }


@dataclass
class Service:
    """A service detected from Docker or process files."""

    name: str
    image: str = ""
    ports: list[str] = field(default_factory=list)
    source: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "image": self.image,
            "ports": self.ports,
            "source": self.source,
        }


@dataclass
class Port:
    """A port binding detected in source code or config."""

    number: int
    label: str = ""
    source: str = ""

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "label": self.label,
            "source": self.source,
        }


@dataclass
class ProjectReport:

    path: str
    languages: list[Language] = field(default_factory=list)
    package_managers: list[PackageManager] = field(default_factory=list)
    env_vars: list[EnvVar] = field(default_factory=list)
    services: list[Service] = field(default_factory=list)
    ports: list[Port] = field(default_factory=list)

    @property
    def total_files(self) -> int:
        """Sum of source files across all detected languages."""
        return sum(lang.file_count for lang in self.languages)

    @property
    def total_lines(self) -> int:
        """Sum of source lines across all detected languages."""
        return sum(lang.line_count for lang in self.languages)

    @property
    def total_dependencies(self) -> int:
        return sum(pm.dependency_count for pm in self.package_managers)

    @property
    def required_env_vars(self) -> list[EnvVar]:
        """Environment variables that have no default value."""
        return [v for v in self.env_vars if v.required]

    @property
    def is_empty(self) -> bool:
        """True when no project configuration was detected at all."""
        return not any([
            self.languages,
            self.package_managers,
            self.env_vars,
            self.services,
            self.ports,
        ])

    def summary(self) -> dict:
        """Return a short summary of the scan for quick display."""
        return {
            "path": self.path,
            "languages_found": len(self.languages),
            "total_source_files": self.total_files,
            "total_source_lines": self.total_lines,
            "package_managers_found": len(self.package_managers),
            "total_dependencies": self.total_dependencies,
            "env_vars_found": len(self.env_vars),
            "required_env_vars": len(self.required_env_vars),
            "services_found": len(self.services),
            "ports_found": len(self.ports),
        }

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "summary": self.summary(),
            "languages": [lang.to_dict() for lang in self.languages],
            "package_managers": [pm.to_dict() for pm in self.package_managers],
            "env_vars": [ev.to_dict() for ev in self.env_vars],
            "services": [svc.to_dict() for svc in self.services],
            "ports": [p.to_dict() for p in self.ports],
        }
