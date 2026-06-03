"""CLI entry point for preflight."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from preflight import __version__
from preflight.formatters.terminal import render_json, render_terminal
from preflight.scanner import scan_project


@click.command()
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("--json", "json_output", is_flag=True, help="JSON output.")
@click.option("--no-color", is_flag=True, help="Disable colored output.")
@click.option("--quiet", "-q", is_flag=True, help="Only show the summary line.")
@click.version_option(version=__version__, prog_name="preflight")
def main(path: str, json_output: bool, no_color: bool, quiet: bool) -> None:
    """Scan a project directory and report everything needed to run it.

    PATH is the directory to scan (defaults to current directory).
    target = Path(path).resolve()

    if not target.is_dir():
        click.echo(f"Error: {target} is not a directory", err=True)
        sys.exit(1)

    report = scan_project(target)

    if json_output:
        click.echo(render_json(report))
    elif quiet:
        parts = []
        if report.languages:
            langs = ", ".join(lang.name for lang in report.languages[:3])
            parts.append(f"languages: {langs}")
        if report.package_managers:
            parts.append(f"package managers: {len(report.package_managers)}")
        if report.env_vars:
            req = len(report.required_env_vars)
            parts.append(f"env vars: {len(report.env_vars)} ({req} required)")
        if report.services:
            parts.append(f"services: {len(report.services)}")
        if report.ports:
            parts.append(f"ports: {len(report.ports)}")
        if parts:
            click.echo(" | ".join(parts))
        else:
            click.echo("No project configuration detected.")
    else:
        render_terminal(report, no_color=no_color)


if __name__ == "__main__":
    main()
