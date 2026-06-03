"""Rich terminal formatter for project scan reports."""

from __future__ import annotations

import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from preflight.models import ProjectReport


def render_json(report: ProjectReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def _build_summary_text(report: ProjectReport) -> str:
    parts = []
    if report.languages:
        parts.append(f"{len(report.languages)} language(s)")
    if report.package_managers:
        dep_count = report.total_dependencies
        if dep_count:
            parts.append(f"{dep_count} dependencies")
        else:
            parts.append(f"{len(report.package_managers)} package manager(s)")
    if report.env_vars:
        req = len(report.required_env_vars)
        parts.append(f"{len(report.env_vars)} env var(s), {req} required")
    if report.services:
        parts.append(f"{len(report.services)} service(s)")
    if report.ports:
        parts.append(f"{len(report.ports)} port(s)")
    return " | ".join(parts) if parts else "No project configuration detected."


def render_terminal(report: ProjectReport, no_color: bool = False) -> None:
    """Render the report to the terminal using Rich panels and tables."""
    console = Console(no_color=no_color)

    console.print()

    # Header panel with path and summary
    header_lines = [
        f"[bold cyan]{report.path}[/bold cyan]",
        f"[dim]{_build_summary_text(report)}[/dim]",
    ]
    console.print(Panel("\n".join(header_lines), title="[bold]preflight[/bold]"))
    console.print()

    # Languages
    if report.languages:
        lang_table = Table(title="Languages", show_header=True)
        lang_table.add_column("Language", style="cyan")
        lang_table.add_column("Extension", style="dim")
        lang_table.add_column("Files", justify="right", style="green")
        lang_table.add_column("Lines", justify="right", style="green")

        for lang in report.languages:
            lines_str = str(lang.line_count) if lang.line_count else ""
            lang_table.add_row(lang.name, lang.extension, str(lang.file_count), lines_str)

        console.print(lang_table)
        console.print()

    # Package Managers
    if report.package_managers:
        for pm in report.package_managers:
            title = f"Package Manager: {pm.name} ({pm.manifest_file})"
            pm_table = Table(title=title, show_header=True)
            pm_table.add_column("Dependency", style="yellow")

            if pm.dependencies:
                for dep in sorted(pm.dependencies):
                    pm_table.add_row(dep)
            else:
                pm_table.add_row(
                    "[dim]No dependencies parsed. Run the package manager to install.[/dim]"
                )

            console.print(pm_table)
            console.print()

    # Environment Variables
    if report.env_vars:
        env_table = Table(title="Environment Variables", show_header=True)
        env_table.add_column("Variable", style="red")
        env_table.add_column("Source", style="dim")
        env_table.add_column("Status", justify="center")

        for var in report.env_vars:
            if var.has_default:
                status = Text("optional", style="green")
            else:
                status = Text("required", style="red bold")
            env_table.add_row(var.name, var.source_file, status)

        console.print(env_table)
        console.print()

    # Services
    if report.services:
        svc_table = Table(title="Services", show_header=True)
        svc_table.add_column("Name", style="magenta")
        svc_table.add_column("Image", style="dim")
        svc_table.add_column("Ports", style="cyan")
        svc_table.add_column("Source", style="dim")

        for svc in report.services:
            ports_str = ", ".join(svc.ports) if svc.ports else ""
            svc_table.add_row(svc.name, svc.image, ports_str, svc.source)

        console.print(svc_table)
        console.print()

    # Ports
    if report.ports:
        port_table = Table(title="Ports", show_header=True)
        port_table.add_column("Port", justify="right", style="cyan")
        port_table.add_column("Label", style="yellow")
        port_table.add_column("Source", style="dim")

        for port in report.ports:
            port_table.add_row(str(port.number), port.label, port.source)

        console.print(port_table)
        console.print()

    # Empty project notice
    if report.is_empty:
        console.print("[dim]No project configuration detected.[/dim]")
        console.print()
