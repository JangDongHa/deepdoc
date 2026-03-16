"""Main scan orchestrator — reads all files and builds the knowledge graph."""

import asyncio
from datetime import datetime, timezone

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from deepdoc.config import DeepDocConfig
from deepdoc.graph.client import close_graphiti_client, create_graphiti_client
from deepdoc.scanner.episode_builder import build_episode
from deepdoc.scanner.file_classifier import discover_and_classify

console = Console()


async def scan(config: DeepDocConfig) -> dict:
    """Exhaustively scan the project and build the knowledge graph.

    Returns a summary dict with scan statistics.
    """
    project_path = config.project.path

    # Phase 1: Discover and classify files
    console.print(f"\n[bold]Scanning[/bold] {project_path}")
    classified_files = discover_and_classify(project_path, config.scan)

    if not classified_files:
        console.print("[yellow]No files found matching scan patterns.[/yellow]")
        return {"files": 0, "episodes": 0, "errors": 0}

    console.print(f"  Found [cyan]{len(classified_files)}[/cyan] files")

    # Show file type breakdown
    type_counts: dict[str, int] = {}
    for f in classified_files:
        key = f.file_type.name.lower()
        type_counts[key] = type_counts.get(key, 0) + 1

    for ftype, count in sorted(type_counts.items()):
        console.print(f"    {ftype}: {count}")

    # Phase 2: Build episodes
    console.print("\n[bold]Building episodes...[/bold]")
    episodes = []
    for cf in classified_files:
        episode = build_episode(cf, project_path)
        if episode:
            episodes.append(episode)

    console.print(f"  Built [cyan]{len(episodes)}[/cyan] episodes")

    # Phase 3: Ingest into Graphiti
    console.print("\n[bold]Ingesting into knowledge graph...[/bold]")
    graphiti = await create_graphiti_client(config)

    errors = 0
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Ingesting...", total=len(episodes))

        for episode in episodes:
            try:
                progress.update(
                    task, description=f"[dim]{episode.name}[/dim]"
                )

                from graphiti_core.nodes import EpisodeType

                await graphiti.add_episode(
                    name=episode.name,
                    episode_body=episode.body,
                    source=EpisodeType.text,
                    source_description=episode.source_description,
                    reference_time=datetime.now(timezone.utc),
                    entity_types=episode.entity_types,
                    edge_types=episode.edge_types,
                    custom_extraction_instructions=episode.extraction_instructions,
                )
            except Exception as e:
                errors += 1
                console.print(
                    f"  [red]Error ingesting {episode.name}: {e}[/red]"
                )

            progress.advance(task)

    await close_graphiti_client(graphiti)

    summary = {
        "files": len(classified_files),
        "episodes": len(episodes),
        "errors": errors,
    }

    console.print(f"\n[bold green]Scan complete.[/bold green]")
    console.print(
        f"  Files: {summary['files']}, "
        f"Episodes: {summary['episodes']}, "
        f"Errors: {summary['errors']}"
    )

    return summary


def run_scan(config: DeepDocConfig) -> dict:
    """Synchronous wrapper for scan()."""
    return asyncio.run(scan(config))
