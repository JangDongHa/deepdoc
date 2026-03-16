"""NestJS-specific framework analysis."""

import re
from pathlib import Path

from deepdoc.scanner.frameworks.base import FrameworkAnalyzer


class NestJSAnalyzer(FrameworkAnalyzer):
    """NestJS framework analyzer.

    Provides enrichment for:
    - Module files: Includes imported module decorators for RouterModule distinction
    - Controller files: Detects route prefixes
    - Guard files: Detects guard types
    """

    def name(self) -> str:
        return "nestjs"

    def enrich_module_episode(
        self, content: str, file_path: Path, project_root: Path
    ) -> str:
        """Extract RouterModule.register blocks and imported module decorators."""
        context_parts = []

        # Extract RouterModule.register block if present
        router_match = re.search(
            r"RouterModule\.register\(\[([\s\S]*?)\]\)",
            content,
        )
        if router_match:
            context_parts.append(
                "=== ROUTER REGISTRATION (CRITICAL) ===\n"
                "Only modules listed here are registered as route children.\n"
                "Modules that exist as directories but are NOT listed here "
                "are NOT registered routes.\n\n"
                f"RouterModule.register([{router_match.group(1)}])"
            )

        # Extract TypeOrmModule connections
        typeorm_matches = re.finditer(
            r"TypeOrmModule\.forRootAsync\(\{([\s\S]*?)\}\)",
            content,
        )
        for match in typeorm_matches:
            name_match = re.search(r"name:\s*['\"](\w+)['\"]", match.group(1))
            db_name = name_match.group(1) if name_match else "default"
            context_parts.append(
                f"=== DATABASE CONNECTION: {db_name} ===\n"
                f"{match.group(0)[:500]}"
            )

        if context_parts:
            return "\n\n" + "\n\n".join(context_parts)
        return ""

    def detect_entity_type(self, file_path: Path, content: str) -> str | None:
        """Detect NestJS entity type from decorators."""
        if "@Module(" in content:
            return "Module"
        if "@Controller(" in content:
            return "Controller"
        if "@Injectable()" in content:
            if "Guard" in file_path.stem or "CanActivate" in content:
                return "Guard"
            if "Interceptor" in file_path.stem:
                return "Interceptor"
            if "Pipe" in file_path.stem:
                return "Pipe"
            if "Filter" in file_path.stem:
                return "Filter"
            if "Repository" in content or "extends Repository" in content:
                return "Repository"
            return "Service"
        if "@Entity(" in content:
            return "Entity"
        return None
