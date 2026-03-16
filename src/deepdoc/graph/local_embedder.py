"""Local code embedder using FastEmbed + Jina Code V2.

Replaces OpenAI embedder — no API key needed, runs fully local.
"""

import logging
from collections.abc import Iterable

from graphiti_core.embedder.client import EmbedderClient, EmbedderConfig

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "jinaai/jina-embeddings-v2-base-code"
DEFAULT_DIM = 768


class LocalCodeEmbedderConfig(EmbedderConfig):
    model: str = DEFAULT_MODEL
    embedding_dim: int = DEFAULT_DIM


class LocalCodeEmbedder(EmbedderClient):
    """Local code embedding using FastEmbed.

    Uses jina-embeddings-v2-base-code (137M params) by default.
    No API key required. Runs on CPU.
    """

    def __init__(self, config: LocalCodeEmbedderConfig | None = None):
        self.config = config or LocalCodeEmbedderConfig()
        self._model = None

    def _get_model(self):
        if self._model is None:
            from fastembed import TextEmbedding

            logger.info(f"Loading embedding model: {self.config.model}")
            self._model = TextEmbedding(
                model_name=self.config.model,
                cache_dir=".deepdoc/models",
            )
        return self._model

    async def create(
        self,
        input_data: str | list[str] | Iterable[int] | Iterable[Iterable[int]],
    ) -> list[float]:
        """Embed a single text string. Returns a flat list of floats."""
        if isinstance(input_data, str):
            texts = [input_data]
        elif isinstance(input_data, list) and input_data and isinstance(input_data[0], str):
            texts = input_data
        else:
            texts = [str(input_data)]

        model = self._get_model()
        embeddings = list(model.embed(texts))
        return embeddings[0].tolist()

    async def create_batch(self, input_data_list: list[str]) -> list[list[float]]:
        """Embed multiple texts. Returns list of embedding vectors."""
        model = self._get_model()
        embeddings = list(model.embed(input_data_list))
        return [e.tolist() for e in embeddings]
