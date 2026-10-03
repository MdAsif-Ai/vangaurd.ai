import uuid


class IngestionService:
    """Placeholder for the Phase 2 ingestion pipeline."""

    async def process_document(self, document_id: uuid.UUID) -> None:
        """Parse, chunk, embed and index a stored document."""
        raise NotImplementedError("Document ingestion is planned for Phase 2.")

    async def reindex_document(self, document_id: uuid.UUID) -> None:
        """Re-run indexing for an existing document."""
        raise NotImplementedError("Reindexing is planned for Phase 2.")
