"""Graphiti client initialization with Kuzu backend."""

import os
from pathlib import Path

from deepdoc.config import DeepDocConfig
from deepdoc.graph.kuzu_patch import patch_kuzu_fts

# Apply FTS index patch before any KuzuDriver is created
patch_kuzu_fts()


async def create_graphiti_client(config: DeepDocConfig):
    """Create and initialize a Graphiti client with Kuzu backend.

    Uses local code embeddings by default (no OpenAI key needed).
    """
    from graphiti_core import Graphiti
    from graphiti_core.driver.kuzu_driver import KuzuDriver

    from deepdoc.graph.local_embedder import LocalCodeEmbedder, LocalCodeEmbedderConfig

    # Ensure graph directory exists
    graph_path = Path(config.graph.path)
    graph_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialize Kuzu driver (embedded, no server)
    driver = KuzuDriver(db=str(graph_path))

    # Initialize LLM client
    llm_client = _create_llm_client(config)

    # Initialize local code embedder (no API key needed)
    embedder = LocalCodeEmbedder(
        config=LocalCodeEmbedderConfig(
            model=config.llm.embedding_model,
            embedding_dim=768,
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


def _create_llm_client(config: DeepDocConfig):
    """Create the appropriate LLM client based on config."""
    provider = config.llm.provider

    if provider == "openai":
        from graphiti_core.llm_client.openai_client import (
            OpenAIClient,
            LLMConfig as OpenAILLMConfig,
        )

        api_key = os.environ.get("OPENAI_API_KEY", "")
        return OpenAIClient(
            config=OpenAILLMConfig(
                api_key=api_key,
                model=config.llm.model,
            )
        )
    elif provider == "anthropic":
        from graphiti_core.llm_client.anthropic_client import (
            AnthropicClient,
            LLMConfig as AnthropicLLMConfig,
        )

        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        return AnthropicClient(
            config=AnthropicLLMConfig(
                api_key=api_key,
                model=config.llm.model,
            )
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


async def close_graphiti_client(graphiti):
    """Clean up Graphiti resources."""
    await graphiti.close()
