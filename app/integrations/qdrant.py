"""Qdrant integration.

The only module that depends on the Qdrant SDK. The future retrieval
layer must talk to this abstraction, never to the SDK directly.
"""

from typing import TYPE_CHECKING

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams

from app.core.config import Settings
from app.core.logging import get_logger

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = get_logger(__name__)

# Default matches BGE-M3-class models; the real dimension is chosen when
# embeddings land in Phase 2 (the collection can be recreated).
DEFAULT_VECTOR_SIZE = 1024


class QdrantIntegration:
    """Thin async wrapper around the Qdrant client."""

    def __init__(self, url: str, api_key: str | None = None, timeout: int = 5) -> None:
        self._client = AsyncQdrantClient(url=url, api_key=api_key, timeout=timeout)

    async def ping(self) -> bool:
        """Return True if Qdrant answers a trivial request."""
        try:
            await self._client.get_collections()
        except Exception:
            return False
        return True

    async def ensure_collection(self, name: str, vector_size: int = DEFAULT_VECTOR_SIZE) -> bool:
        """Create the collection if missing. Returns True if it was created."""
        if await self._client.collection_exists(name):
            return False
        await self._client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        logger.info("Created Qdrant collection %s (vector_size=%s)", name, vector_size)
        return True

    async def close(self) -> None:
        await self._client.close()


def get_qdrant_integration(app: "FastAPI") -> QdrantIntegration:
    """Return the app-scoped Qdrant integration, creating it on first use."""
    integration = getattr(app.state, "qdrant", None)
    if integration is None:
        settings: Settings = app.state.settings
        api_key = settings.qdrant_api_key.get_secret_value() if settings.qdrant_api_key else None
        integration = QdrantIntegration(url=settings.qdrant_url, api_key=api_key)
        app.state.qdrant = integration
    return integration
