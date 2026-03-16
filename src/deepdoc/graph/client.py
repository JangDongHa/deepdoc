"""Graphiti client initialization with Kuzu + Anthropic."""

import os
from pathlib import Path

from deepdoc.config import DeepDocConfig


async def create_graphiti_client(config: DeepDocConfig):
    """Create and initialize a Graphiti client with Kuzu backend."""
    from graphiti_core import Graphiti
    from graphiti_core.driver.kuzu_driver import KuzuDriver
    from graphiti_core.llm_client.anthropic_client import (
        AnthropicClient,
        LLMConfig as AnthropicLLMConfig,
    )
    from graphiti_core.embedder.openai import (
        OpenAIEmbedder,
        OpenAIEmbedderConfig,
    )

    # Ensure graph directory exists
    graph_path = Path(config.graph.path)
    graph_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialize Kuzu driver (embedded, no server)
    driver = KuzuDriver(db=str(graph_path))

    # Initialize Anthropic LLM client
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    llm_client = AnthropicClient(
        config=AnthropicLLMConfig(
            api_key=anthropic_key,
            model=config.llm.model,
        )
    )

    # Initialize OpenAI embedder (required by graphiti)
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    embedder = OpenAIEmbedder(
        config=OpenAIEmbedderConfig(
            api_key=openai_key,
            embedding_model=config.llm.embedding_model,
        )
    )

    # Create Graphiti instance
    graphiti = Graphiti(
        graph_driver=driver,
        llm_client=llm_client,
        embedder=embedder,
    )

    # Build indices
    await graphiti.build_indices_and_constraints()

    return graphiti


async def close_graphiti_client(graphiti):
    """Clean up Graphiti resources."""
    await graphiti.close()
