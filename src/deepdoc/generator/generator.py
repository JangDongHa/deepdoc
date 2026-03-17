"""Documentation generator — queries the graph and produces updoc-compatible markdown."""

from datetime import date
from pathlib import Path

from rich.console import Console

from deepdoc.config import DeepDocConfig
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


def generate(config: DeepDocConfig) -> dict:
    """Generate documentation from the knowledge graph.

    Returns a summary dict with generated file count.
    """
    project_name = config.project.name
    project_path = config.project.path
    output_path = config.output.path
    graph_path = config.graph.path
    head = _get_git_head(project_path)
    today = date.today().isoformat()

    console.print(f"\n[bold]Generating docs[/bold] for {project_name}")

    # Ensure directory structure
    ensure_docs_structure(output_path, project_name)

    # Query ALL facts from graph (no semantic search — direct Kuzu query)
    console.print("  Querying knowledge graph (direct)...")
    query_results = run_all_queries(graph_path)

    total_facts = sum(len(qr.facts) for qr in query_results.values())
    console.print(f"  Retrieved [cyan]{total_facts}[/cyan] categorized facts")

    for section, qr in sorted(query_results.items()):
        if qr.facts:
            console.print(f"    {section}: {len(qr.facts)}")

    # Generate project docs (4 files)
    base = Path(output_path)
    proj_dir = base / "projects" / project_name
    wiki_dir = base / "wiki" / project_name
    files_created = []

    # --- overview.md ---
    overview_parts = []
    routing = query_results.get("routing")
    if routing and routing.facts:
        overview_parts.append(_format_facts_as_markdown(routing.facts, "라우팅 구조"))
    db = query_results.get("database")
    if db and db.facts:
        overview_parts.append(_format_facts_as_markdown(db.facts, "데이터베이스"))
    queues = query_results.get("queues")
    if queues and queues.facts:
        overview_parts.append(_format_facts_as_markdown(queues.facts, "큐/백그라운드"))

    write_updoc_file(
        str(proj_dir / "overview.md"),
        {"project": project_name, "synced_from": head, "synced_at": today},
        f"# {project_name}",
        "\n\n".join(overview_parts) if overview_parts else f"*{project_name} overview — run deepdoc scan first.*",
        [
            "## Sections",
            "",
            "- [Architecture](architecture.md)",
            "- [Configuration](configuration.md)",
            "- [Dependencies](dependencies.md)",
        ],
    )
    files_created.append(f"docs/projects/{project_name}/overview.md")

    # --- architecture.md ---
    arch_parts = []
    modules = query_results.get("modules")
    if modules and modules.facts:
        arch_parts.append(_format_facts_as_markdown(modules.facts, "모듈 구조"))
    if routing and routing.facts:
        arch_parts.append(_format_facts_as_markdown(routing.facts, "라우팅"))

    write_updoc_file(
        str(proj_dir / "architecture.md"),
        {"project": project_name},
        f"# {project_name} — Architecture",
        "\n\n".join(arch_parts) if arch_parts else "*No architecture data.*",
    )
    files_created.append(f"docs/projects/{project_name}/architecture.md")

    # --- configuration.md ---
    cfg_section = query_results.get("configuration")
    write_updoc_file(
        str(proj_dir / "configuration.md"),
        {"project": project_name},
        f"# {project_name} — Configuration",
        _format_facts_as_markdown(cfg_section.facts if cfg_section else [], "설정"),
    )
    files_created.append(f"docs/projects/{project_name}/configuration.md")

    # --- dependencies.md ---
    deps = query_results.get("dependencies")
    db_facts = db.facts if db else []
    all_dep_facts = (deps.facts if deps else []) + db_facts
    write_updoc_file(
        str(proj_dir / "dependencies.md"),
        {"project": project_name},
        f"# {project_name} — Dependencies",
        _format_facts_as_markdown(all_dep_facts, "의존성 & 데이터베이스"),
    )
    files_created.append(f"docs/projects/{project_name}/dependencies.md")

    # --- wiki/index.md ---
    wiki_overview = []
    if modules and modules.facts:
        wiki_overview.append(_format_facts_as_markdown(modules.facts[:10], "서비스 개요"))
    write_updoc_file(
        str(wiki_dir / "index.md"),
        {"project": project_name},
        f"# {project_name} — Wiki",
        "\n\n".join(wiki_overview) if wiki_overview else "*Run deepdoc scan + generate.*",
        [
            "## Pages",
            "",
            "- [Features](features.md)",
            "- [Access](access.md)",
            "- [Policies](policies.md)",
        ],
    )
    files_created.append(f"docs/wiki/{project_name}/index.md")

    # --- wiki/features.md ---
    features_parts = []
    if routing and routing.facts:
        features_parts.append(_format_facts_as_markdown(routing.facts, "엔드포인트"))
    if queues and queues.facts:
        features_parts.append(_format_facts_as_markdown(queues.facts, "백그라운드 처리"))
    write_updoc_file(
        str(wiki_dir / "features.md"),
        {"project": project_name},
        f"# {project_name} — Features",
        "\n\n".join(features_parts) if features_parts else "*No feature data.*",
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
        "# Documentation",
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
    return generate(config)
