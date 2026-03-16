"""CLI entry point for deepdoc."""

import click
from rich.console import Console

from deepdoc.config import load_config

console = Console()


@click.group()
@click.version_option(package_name="deepdoc")
def main():
    """deepdoc — Code knowledge graph → accurate documentation."""
    pass


@main.command()
@click.option(
    "--config",
    "-c",
    default="deepdoc.yaml",
    help="Path to deepdoc.yaml config file",
)
@click.option(
    "--project",
    "-p",
    default=None,
    help="Override project path",
)
def scan(config: str, project: str | None):
    """Exhaustively scan the project and build the knowledge graph."""
    try:
        cfg = load_config(config)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise SystemExit(1)

    if project:
        cfg.project.path = project

    from deepdoc.scanner.scanner import run_scan

    run_scan(cfg)


@main.command()
@click.option(
    "--config",
    "-c",
    default="deepdoc.yaml",
    help="Path to deepdoc.yaml config file",
)
@click.option(
    "--output",
    "-o",
    default=None,
    help="Override output path",
)
def generate(config: str, output: str | None):
    """Generate documentation from the knowledge graph."""
    try:
        cfg = load_config(config)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise SystemExit(1)

    if output:
        cfg.output.path = output

    from deepdoc.generator.generator import run_generate

    run_generate(cfg)


@main.command()
@click.argument("query_text")
@click.option(
    "--config",
    "-c",
    default="deepdoc.yaml",
    help="Path to deepdoc.yaml config file",
)
def query(query_text: str, config: str):
    """Search the knowledge graph with a natural language query."""
    console.print("[yellow]query command not yet implemented (M4)[/yellow]")


@main.command()
@click.argument("doc_path")
@click.option(
    "--config",
    "-c",
    default="deepdoc.yaml",
    help="Path to deepdoc.yaml config file",
)
def verify(doc_path: str, config: str):
    """Verify evidence citations in a document against the graph."""
    console.print("[yellow]verify command not yet implemented (M4)[/yellow]")


if __name__ == "__main__":
    main()
