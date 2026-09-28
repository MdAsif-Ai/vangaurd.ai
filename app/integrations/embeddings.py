"""Embedding provider abstraction.

Phase 1: interface only. A local embedding model (e.g. BGE-M3) or an
external embedding API will be wired in a later phase; no specific model
is forced into the architecture.
"""

from abc import ABC, abstractmethod

from app.core.config import Settings


class EmbeddingError(Exception):
    """Raised when embeddings are unavailable or not implemented."""


class EmbeddingProvider(ABC):
    """Contract for embedding backends."""

    @abstractmethod
    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of document chunks."""

    @abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        """Embed a single query."""


class NotConfiguredEmbeddingProvider(EmbeddingProvider):
    """Placeholder provider until real backends land in Phase 2."""

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        raise EmbeddingError("Embeddings are not implemented yet (planned for Phase 2).")

    async def embed_query(self, text: str) -> list[float]:
        raise EmbeddingError("Embeddings are not implemented yet (planned for Phase 2).")


def get_embedding_provider(settings: Settings) -> EmbeddingProvider:
    """Return the configured embedding provider (placeholder in Phase 1)."""
    return NotConfiguredEmbeddingProvider()