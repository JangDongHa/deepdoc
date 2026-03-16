"""Build Graphiti episodes from source files."""

import re
from dataclasses import dataclass
from pathlib import Path

from deepdoc.scanner.file_classifier import ClassifiedFile, FileType
from deepdoc.schema.entities import EntityType
from deepdoc.schema.edges import EdgeType


@dataclass
class Episode:
    """A structured chunk for Graphiti ingestion."""

    name: str
    body: str
    source_description: str
    entity_types: dict
    edge_types: dict


# Map FileType to the primary EntityType expected in that file
FILE_TYPE_TO_ENTITY: dict[FileType, EntityType] = {
    FileType.MODULE: EntityType.MODULE,
    FileType.CONTROLLER: EntityType.CONTROLLER,
    FileType.SERVICE: EntityType.SERVICE,
    FileType.REPOSITORY: EntityType.REPOSITORY,
    FileType.GUARD: EntityType.GUARD,
    FileType.ENTITY: EntityType.ENTITY,
    FileType.DTO: EntityType.DTO,
    FileType.SPEC: EntityType.SPEC,
    FileType.CONFIG: EntityType.CONFIG,
    FileType.DECORATOR: EntityType.DECORATOR,
    FileType.PIPE: EntityType.PIPE,
    FileType.INTERCEPTOR: EntityType.INTERCEPTOR,
    FileType.FILTER: EntityType.FILTER,
}

# Map FileType to the edge types likely to appear
FILE_TYPE_TO_EDGES: dict[FileType, list[EdgeType]] = {
    FileType.MODULE: [
        EdgeType.IMPORTS_MODULE,
        EdgeType.REGISTERS_IN_ROUTER,
        EdgeType.EXPORTS_MODULE,
        EdgeType.PROVIDES,
        EdgeType.CONNECTS_TO_DB,
        EdgeType.REGISTERS_ENTITY,
    ],
    FileType.CONTROLLER: [
        EdgeType.DEFINES_ROUTE,
        EdgeType.USES_GUARD,
        EdgeType.USES_DECORATOR,
        EdgeType.INJECTS,
    ],
    FileType.SERVICE: [
        EdgeType.INJECTS,
        EdgeType.CALLS,
        EdgeType.VALIDATES_WITH,
        EdgeType.QUEUES_JOB,
    ],
    FileType.GUARD: [
        EdgeType.INJECTS,
        EdgeType.CALLS,
    ],
    FileType.SPEC: [
        EdgeType.VALIDATES_WITH,
        EdgeType.CALLS,
    ],
    FileType.ROOT_MODULE: [
        EdgeType.IMPORTS_MODULE,
        EdgeType.REGISTERS_IN_ROUTER,
        EdgeType.PROVIDES,
        EdgeType.CONNECTS_TO_DB,
        EdgeType.REGISTERS_ENTITY,
    ],
}


def _extract_imports(content: str, project_root: Path, file_path: Path) -> list[Path]:
    """Extract local import paths from TypeScript source."""
    imports = []
    pattern = r"""from\s+['"](@/[^'"]+|\.\.?/[^'"]+)['"]"""
    for match in re.finditer(pattern, content):
        import_path = match.group(1)
        if import_path.startswith("@/"):
            resolved = project_root / "src" / import_path[2:]
        else:
            resolved = (file_path.parent / import_path).resolve()

        # Try .ts extension
        for ext in [".ts", "/index.ts"]:
            candidate = Path(str(resolved) + ext)
            if candidate.exists():
                imports.append(candidate)
                break
    return imports


def _build_module_context(
    content: str, project_root: Path, file_path: Path
) -> str:
    """Build enriched context for module files.

    Includes summaries of imported modules so the LLM can distinguish
    IMPORTS_MODULE from REGISTERS_IN_ROUTER.
    """
    imported_files = _extract_imports(content, project_root, file_path)
    context_parts = []

    for imp in imported_files:
        if not imp.name.endswith(".module.ts"):
            continue
        try:
            imp_content = imp.read_text(encoding="utf-8")
            # Extract just the @Module decorator block
            module_match = re.search(
                r"@Module\(\{[\s\S]*?\}\)\s*export\s+class\s+\w+",
                imp_content,
            )
            if module_match:
                relative = str(imp.relative_to(project_root))
                context_parts.append(
                    f"--- {relative} (module decorator) ---\n"
                    f"{module_match.group(0)}"
                )
        except (OSError, UnicodeDecodeError):
            continue

    if context_parts:
        return "\n\n=== IMPORTED MODULE SUMMARIES ===\n\n" + "\n\n".join(
            context_parts
        )
    return ""


def build_episode(
    classified: ClassifiedFile,
    project_root: str,
) -> Episode | None:
    """Build a Graphiti episode from a classified file."""
    root = Path(project_root).resolve()

    try:
        content = classified.path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    # Skip empty files
    if not content.strip():
        return None

    # Build episode body
    body = f"=== FILE: {classified.relative_path} ===\n\n{content}"

    # Enrich module files with imported module context
    if classified.file_type in (FileType.MODULE, FileType.ROOT_MODULE):
        module_context = _build_module_context(content, root, classified.path)
        if module_context:
            body += "\n\n" + module_context

    # Determine relevant entity and edge types for this file
    entity_type = FILE_TYPE_TO_ENTITY.get(classified.file_type)
    edge_types = FILE_TYPE_TO_EDGES.get(classified.file_type, [])

    # Build type hints for Graphiti
    from deepdoc.schema.entities import CodeEntity
    from deepdoc.schema.edges import CodeRelationship

    entity_hints = {}
    if entity_type:
        entity_hints[entity_type.value] = CodeEntity

    edge_hints = {}
    for et in edge_types:
        edge_hints[et.value] = CodeRelationship

    return Episode(
        name=f"file:{classified.relative_path}",
        body=body,
        source_description=(
            f"{classified.file_type.name.lower()} file: {classified.relative_path}"
        ),
        entity_types=entity_hints,
        edge_types=edge_hints,
    )
