import uuid
from typing import TypedDict


class RetrievedChunk(TypedDict):
    document_id: uuid.UUID
    chunk_id: str
    text: str
    score: float


class RetrievalService:
    """Placeholder for the hybrid retrieval pipeline."""

    async def retrieve(
        self,
        query: str,
        *,
        organization_id: uuid.UUID,
        document_ids: list[uuid.UUID] | None = None,
    ) -> list[RetrievedChunk]:
        raise NotImplementedError("Hybrid retrieval is planned for a later phase.")