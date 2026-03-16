"""Documentation generator — queries the graph and produces updoc-compatible markdown."""

import asyncio
import os
from datetime import date
from pathlib import Path

from rich.console import Console

from deepdoc.config import DeepDocConfig
from deepdoc.graph.client import create_graphiti_client, close_graphiti_client
from deepdoc.graph.queries import run_all_queries
from deepdoc.generator.updoc_compat import ensure_docs_structure, write_updoc_file

console = Console()


def _get_git_head(project_path: str) -> str:
    """Get the short HEAD commit hash of the project."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _format_facts_as_markdown(facts: list[str], header: str = "") -> str:
    """Format a list of graph facts as markdown bullets."""
    if not facts:
        return f"*No data found for {header}.*" if header else ""

    lines = []
    if header:
        lines.append(f"## {header}")
        lines.append("")
    for fact in facts:
        lines.append(f"- {fact}")
    return "\n".join(lines)


async def generate(config: DeepDocConfig) -> dict:
    """Generate documentation from the knowledge graph.

    Returns a summary dict with generated file count.
    """
    project_name = config.project.name
    project_path = config.project.path
    output_path = config.output.path
    head = _get_git_head(project_path)
    today = date.today().isoformat()

    console.print(f"\n[bold]Generating docs[/bold] for {project_name}")

    # Ensure directory structure
    ensure_docs_structure(output_path, project_name)

    # Connect to graph and run queries
    console.print("  Querying knowledge graph...")
    graphiti = await create_graphiti_client(config)
    query_results = await run_all_queries(graphiti)
    await close_graphiti_client(graphiti)

    total_facts = sum(len(qr.facts) for qr in query_results.values())
    console.print(f"  Retrieved [cyan]{total_facts}[/cyan] facts from graph")

    # Generate project docs (4 files)
    base = Path(output_path)
    proj_dir = base / "projects" / project_name
    wiki_dir = base / "wiki" / project_name
    files_created = []

    # --- overview.md ---
    routing = query_results.get("routing")
    overview_parts = []
    if routing:
        overview_parts.append(_format_facts_as_markdown(routing.facts, "라우팅 구조"))
    db = query_results.get("database")
    if db:
        overview_parts.append(_format_facts_as_markdown(db.facts, "데이터베이스"))
    queues = query_results.get("queues")
    if queues:
        overview_parts.append(_format_facts_as_markdown(queues.facts, "큐/백그라운드"))

    write_updoc_file(
        str(proj_dir / "overview.md"),
        {"project": project_name, "synced_from": head, "synced_at": today},
        f"# {project_name}",
        "\n\n".join(overview_parts),
        ["## Sections", "", "- [Architecture](architecture.md)", "- [Configuration](configuration.md)", "- [Dependencies](dependencies.md)"],
    )
    files_created.append(f"docs/projects/{project_name}/overview.md")

    # --- architecture.md ---
    arch_parts = []
    if routing:
        arch_parts.append(_format_facts_as_markdown(routing.facts, "라우팅 구조"))
    controllers = query_results.get("controllers")
    if controllers:
        arch_parts.append(_format_facts_as_markdown(controllers.facts, "컨트롤러 & 엔드포인트"))

    write_updoc_file(
        str(proj_dir / "architecture.md"),
        {"project": project_name},
        f"# {project_name} — Architecture",
        "\n\n".join(arch_parts),
    )
    files_created.append(f"docs/projects/{project_name}/architecture.md")

    # --- configuration.md ---
    cfg = query_results.get("configuration")
    write_updoc_file(
        str(proj_dir / "configuration.md"),
        {"project": project_name},
        f"# {project_name} — Configuration",
        _format_facts_as_markdown(cfg.facts if cfg else [], "설정"),
    )
    files_created.append(f"docs/projects/{project_name}/configuration.md")

    # --- dependencies.md ---
    deps = query_results.get("dependencies")
    write_updoc_file(
        str(proj_dir / "dependencies.md"),
        {"project": project_name},
        f"# {project_name} — Dependencies",
        _format_facts_as_markdown(deps.facts if deps else [], "의존성"),
    )
    files_created.append(f"docs/projects/{project_name}/dependencies.md")

    # --- wiki/index.md ---
    wiki_overview = []
    if routing:
        wiki_overview.append(_format_facts_as_markdown(routing.facts[:5], "서비스 개요"))
    write_updoc_file(
        str(wiki_dir / "index.md"),
        {"project": project_name},
        f"# {project_name} — Wiki",
        "\n\n".join(wiki_overview),
        ["## Pages", "", "- [Features](features.md)", "- [Access](access.md)", "- [Policies](policies.md)"],
    )
    files_created.append(f"docs/wiki/{project_name}/index.md")

    # --- wiki/features.md ---
    features_parts = []
    if controllers:
        features_parts.append(_format_facts_as_markdown(controllers.facts, "기능"))
    if queues:
        features_parts.append(_format_facts_as_markdown(queues.facts, "백그라운드 처리"))
    write_updoc_file(
        str(wiki_dir / "features.md"),
        {"project": project_name},
        f"# {project_name} — Features",
        "\n\n".join(features_parts),
    )
    files_created.append(f"docs/wiki/{project_name}/features.md")

    # --- wiki/access.md ---
    auth = query_results.get("auth")
    write_updoc_file(
        str(wiki_dir / "access.md"),
        {"project": project_name},
        f"# {project_name} — Access",
        _format_facts_as_markdown(auth.facts if auth else [], "인증 & 접근"),
    )
    files_created.append(f"docs/wiki/{project_name}/access.md")

    # --- wiki/policies.md ---
    rules = query_results.get("business_rules")
    write_updoc_file(
        str(wiki_dir / "policies.md"),
        {"project": project_name},
        f"# {project_name} — Policies",
        _format_facts_as_markdown(rules.facts if rules else [], "비즈니스 규칙"),
    )
    files_created.append(f"docs/wiki/{project_name}/policies.md")

    # --- docs/index.md ---
    index_content = (
        f"| Project | Wiki | Technical |\n"
        f"|---------|------|-----------|\n"
        f"| {project_name} | [wiki/{project_name}/index.md](wiki/{project_name}/index.md) "
        f"| [projects/{project_name}/overview.md](projects/{project_name}/overview.md) |"
    )
    write_updoc_file(
        str(base / "index.md"),
        {},
        f"# Documentation",
        index_content,
        ["[Missions](missions/)"],
    )
    files_created.append("docs/index.md")

    # Report
    console.print(f"\n[bold green]Generation complete.[/bold green]")
    for f in files_created:
        console.print(f"  📄 {f}")

    return {"files": len(files_created), "facts": total_facts}


def run_generate(config: DeepDocConfig) -> dict:
    """Synchronous wrapper for generate()."""
    return asyncio.run(generate(config))
