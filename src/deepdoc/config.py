"""YAML configuration loader for deepdoc."""

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class LLMConfig:
    provider: str = "anthropic"
    model: str = "claude-sonnet-4-20250514"
    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"


@dataclass
class ScanConfig:
    include: list[str] = field(default_factory=lambda: ["src/**/*.ts"])
    exclude: list[str] = field(
        default_factory=lambda: [
            "**/*.e2e.spec.ts",
            "**/node_modules/**",
            "**/dist/**",
        ]
    )


@dataclass
class OutputConfig:
    path: str = "./docs"
    format: str = "updoc"
    language: str = "en"


@dataclass
class ProjectConfig:
    name: str = ""
    path: str = "."
    language: str = "typescript"
    framework: str = "nestjs"


@dataclass
class GraphConfig:
    path: str = ".deepdoc/graph.kuzu"


@dataclass
class DeepDocConfig:
    version: str = "0.1.0"
    project: ProjectConfig = field(default_factory=ProjectConfig)
    graph: GraphConfig = field(default_factory=GraphConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    scan: ScanConfig = field(default_factory=ScanConfig)
    output: OutputConfig = field(default_factory=OutputConfig)


def load_config(config_path: str = "deepdoc.yaml") -> DeepDocConfig:
    """Load configuration from YAML file."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path) as f:
        raw = yaml.safe_load(f)

    config = DeepDocConfig(version=raw.get("version", "0.1.0"))

    if "project" in raw:
        p = raw["project"]
        config.project = ProjectConfig(
            name=p.get("name", ""),
            path=p.get("path", "."),
            language=p.get("language", "typescript"),
            framework=p.get("framework", "nestjs"),
        )

    if "graph" in raw:
        config.graph = GraphConfig(path=raw["graph"].get("path", ".deepdoc/graph.kuzu"))

    if "llm" in raw:
        l = raw["llm"]
        config.llm = LLMConfig(
            provider=l.get("provider", "anthropic"),
            model=l.get("model", "claude-sonnet-4-20250514"),
            embedding_provider=l.get("embedding_provider", "openai"),
            embedding_model=l.get("embedding_model", "text-embedding-3-small"),
        )

    if "scan" in raw:
        s = raw["scan"]
        config.scan = ScanConfig(
            include=s.get("include", ["src/**/*.ts"]),
            exclude=s.get("exclude", []),
        )

    if "output" in raw:
        o = raw["output"]
        config.output = OutputConfig(
            path=o.get("path", "./docs"),
            format=o.get("format", "updoc"),
            language=o.get("language", "en"),
        )

    return config
