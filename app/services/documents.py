"""Document management service (database-level operations in Phase 1).

File upload, parsing, embedding and Qdrant indexing are Phase 2; this
service only manages the document registry in the organization scope.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document, DocumentStatus
from app.db.repositories import AuditLogRepository, DocumentRepository
from app.schemas.documents import DocumentCreate


def _storage_key(organization_id: uuid.UUID, document_id: uuid.UUID) -> str:
    return f"{organization_id}/{document_id}"


class DocumentService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._documents = DocumentRepository(session)
        self._audit = AuditLogRepository(session)

    async def create(
        self,
        *,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        data: DocumentCreate,
    ) -> Document:
        """Register a document record with status 'uploaded'."""
        document_id = uuid.uuid4()
        document = Document(
            id=document_id,
            organization_id=organization_id,
            name=data.name,
            company=data.company,
            document_type=data.document_type,
            fiscal_year=data.fiscal_year,
            checksum=data.checksum,
            storage_key=_storage_key(organization_id, document_id),
            status=DocumentStatus.UPLOADED,
        )
        await self._documents.create(document)
        await self._audit.log(
            organization_id=organization_id,
            user_id=user_id,
            action="document.created",
            resource_type="document",
            resource_id=str(document_id),
            meta={"name": data.name},
        )
        await self._session.commit()
        return document

    async def get(self, *, organization_id: uuid.UUID, document_id: uuid.UUID) -> Document | None:
        return await self._documents.get(organization_id, document_id)

    async def list_documents(
        self, *, organization_id: uuid.UUID, skip: int, limit: int
    ) -> tuple[list[Document], int]:
        return await self._documents.list_documents(organization_id, skip=skip, limit=limit)

    async def delete(
        self,
        *,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        document: Document,
    ) -> None:
        """Delete the document record (cascades to versions/facts/evidence).

        Stored files are removed when ingestion lands in Phase 2.
        """
        await self._documents.delete(document)
        await self._audit.log(
            organization_id=organization_id,
            user_id=user_id,
            action="document.deleted",
            resource_type="document",
            resource_id=str(document.id),
        )
        await self._session.commit()
