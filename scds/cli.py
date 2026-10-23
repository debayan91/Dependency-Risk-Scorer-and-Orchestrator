"""
Developer Command Line Interface (CLI) for SCDS.
Features rich terminal formatting, color-coded risk badges, and CI/CD build-gate exit codes.
"""

import json
import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from scds import __version__
from scds.engine import RiskEngine
from scds.parsers import Dependency, parse_manifest

console = Console()


def get_badge(level: str) -> str:
    """Returns styled colored badge for terminal output."""
    if level == "SAFE":
        return "[bold green]SAFE[/bold green]"
    elif level == "LOW":
        return "[bold cyan]LOW[/bold cyan]"
    elif level == "MEDIUM":
        return "[bold yellow]MEDIUM[/bold yellow]"
    elif level == "HIGH":
        return "[bold magenta]HIGH[/bold magenta]"
    elif level == "CRITICAL":
        return "[bold white on red] CRITICAL [/bold white on red]"
    return level


def render_report_table(report) -> None:
    """Renders formatted Rich tables and summary panels."""
    console.print()
    console.print(
        Panel.fit(
            f"[bold cyan]Supply Chain Dependency Risk Scorer (SCDS) v{__version__}[/bold cyan]\n"
            f"[dim]Deterministic, explainable supply chain threat analysis[/dim]\n"
            f"Target: [bold yellow]{report.target_manifest}[/bold yellow] | Ecosystem: [bold]{report.ecosystem}[/bold]",
            border_style="cyan"
        )
    )

    table = Table(title="Dependency Risk Assessment", show_header=True, header_style="bold cyan", expand=True)
    table.add_column("Package", style="bold", no_wrap=True)
    table.add_column("Version", style="dim", no_wrap=True)
    table.add_column("Score", justify="right")
    table.add_column("Risk Level", justify="center")
    table.add_column("Key Findings / Explanations", ratio=2)

    for r in report.results:
        score_style = "green"
        if r.total_risk_score >= 9.0:
            score_style = "bold red"
        elif r.total_risk_score >= 7.5:
            score_style = "bold magenta"
        elif r.total_risk_score >= 5.5:
            score_style = "bold yellow"
        elif r.total_risk_score >= 3.0:
            score_style = "cyan"

        finding_text = "\n".join(r.findings[:2])
        if len(r.findings) > 2:
            finding_text += f"\n[dim]+ {len(r.findings) - 2} more findings...[/dim]"

        table.add_row(
            r.dependency.name,
            r.dependency.version or "[dim]unspecified[/dim]",
            f"[{score_style}]{r.total_risk_score:.1f}[/{score_style}]",
            get_badge(r.risk_level),
            finding_text
        )

    console.print(table)

    # Summary Panel
    s = report.risk_summary
    summary_text = (
        f"Total Scanned: [bold]{report.dependencies_scanned}[/bold] | "
        f"[green]Safe: {s.get('SAFE', 0)}[/green] | "
        f"[cyan]Low: {s.get('LOW', 0)}[/cyan] | "
        f"[yellow]Medium: {s.get('MEDIUM', 0)}[/yellow] | "
        f"[magenta]High: {s.get('HIGH', 0)}[/magenta] | "
        f"[bold red]Critical: {s.get('CRITICAL', 0)}[/bold red]\n"
        f"Average Score: [bold]{report.avg_risk_score:.1f}/10[/bold] | "
        f"Peak Score: [bold]{report.max_risk_score:.1f}/10[/bold]"
    )

    status_title = "[bold green]✓ PASSED CI/CD POLICY GATE[/bold green]"
    border_color = "green"

    if report.failed_ci:
        status_title = "[bold white on red] ✗ FAILED CI/CD POLICY GATE [/bold white on red]"
        border_color = "red"
        summary_text += f"\n\n[bold red]FAILURE REASON:[/bold red] {report.fail_reason}"

    console.print(Panel(summary_text, title=status_title, border_style=border_color))
    console.print()


@click.group()
@click.version_option(version=__version__)
def cli():
    """Supply Chain Dependency Risk Scorer (SCDS) CLI."""
    pass


@cli.command(name="scan")
@click.argument("manifest_path", type=click.Path(exists=True))
@click.option("--fail-on", type=click.Choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"], case_sensitive=False),
              help="Break build and exit with code 1 if risk meets or exceeds this level.")
@click.option("--threshold", type=float, default=None,
              help="Break build and exit with code 1 if any package exceeds this score (0.0 - 10.0).")
@click.option("--format", "output_format", type=click.Choice(["table", "json"]), default="table",
              help="Output presentation format.")
@click.option("--output", "output_file", type=click.Path(), default=None,
              help="Export JSON report to specified file path.")
@click.option("--no-cache", is_flag=True, default=False,
              help="Bypass local cache and query upstream registries directly.")
def scan_command(manifest_path: str, fail_on: Optional[str], threshold: Optional[float],
                 output_format: str, output_file: Optional[str], no_cache: bool):
    """
    Scans a dependency manifest (package.json, requirements.txt, pom.xml).
    """
    try:
        deps = parse_manifest(manifest_path)
    except Exception as e:
        console.print(f"[bold red]Error parsing manifest:[/bold red] {str(e)}")
        sys.exit(2)

    if not deps:
        console.print(f"[yellow]No dependencies discovered in {manifest_path}.[/yellow]")
        sys.exit(0)

    engine = RiskEngine(cache_enabled=not no_cache)
    report = engine.scan_dependencies(
        dependencies=deps,
        manifest_name=Path(manifest_path).name,
        fail_on_level=fail_on,
        fail_threshold=threshold
    )

    if output_format == "json":
        json_output = json.dumps(report.to_dict(), indent=2)
        console.print(json_output)
    else:
        render_report_table(report)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2)
        console.print(f"[dim]Report saved to {output_file}[/dim]")

    # Exit with appropriate CI/CD exit code
    if report.failed_ci:
        sys.exit(1)
    sys.exit(0)


@cli.command(name="check")
@click.argument("package_name")
@click.option("--version", "-v", default=None, help="Specific version to evaluate.")
@click.option("--ecosystem", "-e", type=click.Choice(["PyPI", "npm", "Maven"], case_sensitive=False),
              default="PyPI", help="Package registry ecosystem.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Print output as JSON.")
def check_command(package_name: str, version: Optional[str], ecosystem: str, as_json: bool):
    """
    Quickly checks a single package for typosquatting, vulnerabilities, and maintainer posture.
    """
    dep = Dependency(name=package_name, version=version, ecosystem=ecosystem)
    engine = RiskEngine(cache_enabled=True)
    report = engine.evaluate_dependency(dep)

    if as_json:
        console.print(json.dumps(report.to_dict(), indent=2))
        return

    console.print()
    console.print(Panel(
        f"Package: [bold]{dep.name}[/bold] | Version: [bold]{dep.version or 'latest'}[/bold] | Ecosystem: [bold]{dep.ecosystem}[/bold]\n"
        f"Score: [bold]{report.total_risk_score}/10[/bold] ({get_badge(report.risk_level)})\n\n"
        f"[bold]Findings:[/bold]\n" + "\n".join(f"• {f}" for f in report.findings) +
        ("\n\n[bold]Recommendations:[/bold]\n" + "\n".join(f"→ {r}" for r in report.recommendations) if report.recommendations else ""),
        title=f"SCDS Single Package Audit: {package_name}",
        border_style="cyan"
    ))
    console.print()


@cli.command(name="dashboard")
@click.option("--host", default="127.0.0.1", help="Host interface to bind dashboard.")
@click.option("--port", default=8000, type=int, help="Port to run the dashboard server.")
def dashboard_command(host: str, port: int):
    """
    Launches the interactive Web Dashboard.
    """
    import uvicorn
    console.print(f"[bold cyan]Launching SCDS Web Dashboard on http://{host}:{port}...[/bold cyan]")
    uvicorn.run("scds.web.app:app", host=host, port=port, log_level="info")


if __name__ == "__main__":
    cli()
