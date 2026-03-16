"""updoc-compatible markdown file writer.

Handles frontmatter, marker blocks, and file structure
matching updoc's output format.
"""

from pathlib import Path


def write_updoc_file(
    path: str,
    frontmatter: dict,
    title: str,
    managed_content: str,
    static_sections: list[str] | None = None,
):
    """Write a markdown file with updoc marker blocks and frontmatter.

    Args:
        path: Output file path
        frontmatter: YAML frontmatter dict (project, synced_from, synced_at)
        title: Document title (e.g. "# modu-api-partner")
        managed_content: Content inside <!-- updoc:begin/end --> markers
        static_sections: Content after the markers (user-editable sections)
    """
    filepath = Path(path)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    lines = ["---"]
    for k, v in frontmatter.items():
        lines.append(f"{k}: {v}")
    lines.append("---")
    lines.append("")
    lines.append(title)
    lines.append("")
    lines.append("<!-- updoc:begin -->")
    lines.append("")
    lines.append(managed_content)
    lines.append("")
    lines.append("<!-- updoc:end -->")

    if static_sections:
        for section in static_sections:
            lines.append("")
            lines.append(section)

    lines.append("")

    filepath.write_text("\n".join(lines), encoding="utf-8")


def ensure_docs_structure(output_path: str, project_name: str):
    """Create the updoc directory structure."""
    base = Path(output_path)
    dirs = [
        base / "projects" / project_name,
        base / "wiki" / project_name,
        base / "missions",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
