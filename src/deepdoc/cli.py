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
    import asyncio
    from deepdoc.graph.client import create_graphiti_client, close_graphiti_client

    try:
        cfg = load_config(config)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise SystemExit(1)

    async def _query():
        graphiti = await create_graphiti_client(cfg)
        results = await graphiti.search(query_text)
        await close_graphiti_client(graphiti)
        return results

    results = asyncio.run(_query())

    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return

    console.print(f"\n[bold]{len(results)} results:[/bold]")
    for r in results:
        console.print(f"  • {r.fact}")


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
    try:
        cfg = load_config(config)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise SystemExit(1)

    from deepdoc.verifier.verifier import run_verify

    run_verify(cfg, doc_path)


if __name__ == "__main__":
    main()
