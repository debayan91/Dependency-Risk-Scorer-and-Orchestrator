"""Command-line boundary for local runs and CI jobs."""

import json
import sys
from pathlib import Path
from typing import Optional, Sequence

import click

from orchestrator.policy import Policy
from orchestrator.service import RepositoryScanner


@click.command()
@click.argument("repository", type=click.Path(exists=True, file_okay=False, path_type=Path), default=".")
@click.option("--changed", "changed_paths", multiple=True, type=click.Path(),
              help="Scan only this changed manifest path; repeat for multiple paths.")
@click.option("--warn-on", default="MEDIUM", show_default=True,
              type=click.Choice(["SAFE", "LOW", "MEDIUM", "HIGH", "CRITICAL"], case_sensitive=False))
@click.option("--block-on", default="CRITICAL", show_default=True,
              type=click.Choice(["SAFE", "LOW", "MEDIUM", "HIGH", "CRITICAL"], case_sensitive=False))
@click.option("--no-cache", is_flag=True, help="Query upstream services instead of using SCDS cache.")
def cli(repository: Path, changed_paths: Sequence[str], warn_on: str, block_on: Optional[str], no_cache: bool) -> None:
    """Discover and scan dependency manifests for a repository."""
    scanner = RepositoryScanner(
        policy=Policy(warn_on=warn_on, block_on=block_on), cache_enabled=not no_cache
    )
    result = (
        scanner.scan_changed_files(repository, changed_paths)
        if changed_paths else scanner.scan_repository(repository)
    )
    click.echo(json.dumps(result.to_dict(), indent=2))
    if result.decision.status == "BLOCK":
        sys.exit(1)


if __name__ == "__main__":
    cli()
