"""Classify source files by type and determine scan order."""

from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path

from deepdoc.config import ScanConfig


class FileType(IntEnum):
    """File types ordered by scan priority (leaves first, root last)."""

    CONFIG = 0
    ENTITY = 1
    DTO = 2
    SPEC = 3
    REPOSITORY = 4
    SERVICE = 5
    GUARD = 6
    DECORATOR = 7
    PIPE = 8
    INTERCEPTOR = 9
    FILTER = 10
    CONTROLLER = 11
    MODULE = 12
    ROOT_MODULE = 13
    ENTRY_POINT = 14
    OTHER = 99


# NestJS file suffix → FileType mapping
NESTJS_SUFFIXES: dict[str, FileType] = {
    ".entity.ts": FileType.ENTITY,
    ".dto.ts": FileType.DTO,
    ".spec.ts": FileType.SPEC,
    ".repo.ts": FileType.REPOSITORY,
    ".service.ts": FileType.SERVICE,
    ".guard.ts": FileType.GUARD,
    ".decorator.ts": FileType.DECORATOR,
    ".pipe.ts": FileType.PIPE,
    ".interceptor.ts": FileType.INTERCEPTOR,
    ".filter.ts": FileType.FILTER,
    ".controller.ts": FileType.CONTROLLER,
    ".module.ts": FileType.MODULE,
}

CONFIG_FILES = {
    "package.json",
    "tsconfig.json",
    "tsconfig.build.json",
    "nest-cli.json",
    ".nvmrc",
    ".prettierrc",
}

ROOT_FILES = {"app.module.ts", "main.ts"}


@dataclass
class ClassifiedFile:
    path: Path
    file_type: FileType
    relative_path: str


def classify_file(file_path: Path, project_root: Path) -> FileType:
    """Classify a single file by its name/suffix."""
    name = file_path.name
    relative = str(file_path.relative_to(project_root))

    if name in CONFIG_FILES:
        return FileType.CONFIG

    if name == "main.ts":
        return FileType.ENTRY_POINT

    if name == "app.module.ts":
        return FileType.ROOT_MODULE

    # Check NestJS suffixes (longest match first)
    for suffix, file_type in sorted(
        NESTJS_SUFFIXES.items(), key=lambda x: -len(x[0])
    ):
        if name.endswith(suffix):
            # Exclude e2e test files
            if suffix == ".spec.ts" and ".e2e." in name:
                return FileType.OTHER
            return file_type

    if name.endswith(".ts"):
        return FileType.OTHER

    return FileType.OTHER


def discover_and_classify(
    project_root: str, scan_config: ScanConfig
) -> list[ClassifiedFile]:
    """Discover all files matching include patterns, classify, and sort by scan order."""
    root = Path(project_root).resolve()
    files: list[ClassifiedFile] = []

    for pattern in scan_config.include:
        for file_path in root.glob(pattern):
            if not file_path.is_file():
                continue

            relative = str(file_path.relative_to(root))

            # Check exclude patterns
            excluded = False
            for exc in scan_config.exclude:
                if file_path.match(exc):
                    excluded = True
                    break
            if excluded:
                continue

            file_type = classify_file(file_path, root)
            files.append(
                ClassifiedFile(
                    path=file_path,
                    file_type=file_type,
                    relative_path=relative,
                )
            )

    # Sort by file_type (scan order), then by path for determinism
    files.sort(key=lambda f: (f.file_type.value, f.relative_path))
    return files
