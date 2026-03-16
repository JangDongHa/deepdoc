"""Abstract base class for framework-specific analysis."""

from abc import ABC, abstractmethod
from pathlib import Path


class FrameworkAnalyzer(ABC):
    """Base class for framework-specific code analysis.

    Subclasses provide framework-specific hints for episode enrichment,
    entity type detection, and relationship extraction.
    """

    @abstractmethod
    def name(self) -> str:
        """Framework identifier (e.g. 'nestjs', 'spring')."""
        ...

    @abstractmethod
    def enrich_module_episode(
        self, content: str, file_path: Path, project_root: Path
    ) -> str:
        """Add framework-specific context to module file episodes.

        Returns additional context string to append to the episode body.
        """
        ...

    @abstractmethod
    def detect_entity_type(self, file_path: Path, content: str) -> str | None:
        """Detect the primary entity type from file content.

        Returns an EntityType value string, or None if unknown.
        """
        ...
