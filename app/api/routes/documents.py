"""Document registry API (database-level operations only in Phase 1)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencies import CurrentUser, DbSession
from app.schemas.common import MessageResponse
from app.schemas.documents import DocumentCreate, DocumentListResponse, DocumentResponse
from app.services.documents import DocumentService

router = APIRouter()


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    body: DocumentCreate, session: DbSession, current_user: CurrentUser
) -> DocumentResponse:
    """Register a document record in the caller's organization.

    File upload, parsing and indexing arrive in Phase 2.
    """
    document = await DocumentService(session).create(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        data=body,
    )
    return DocumentResponse.model_validate(document)


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    session: DbSession,
    current_user: CurrentUser,
    skip: Annotated[int, Query(default=0, ge=0)],
    limit: Annotated[int, Query(default=20, ge=1, le=100)],
) -> DocumentListResponse:
    """List documents in the caller's organization (paginated)."""
    documents, total = await DocumentService(session).list_documents(
        organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(document) for document in documents],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID, session: DbSession, current_user: CurrentUser
) -> DocumentResponse:
    document = await DocumentService(session).get(
        organization_id=current_user.organization_id, document_id=document_id
    )
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentResponse.model_validate(document)


@router.delete("/{document_id}", response_model=MessageResponse)
async def delete_document(
    document_id: uuid.UUID, session: DbSession, current_user: CurrentUser
) -> MessageResponse:
    document = await DocumentService(session).get(
        organization_id=current_user.organization_id, document_id=document_id
    )
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    await DocumentService(session).delete(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        document=document,
    )
    return MessageResponse(
        message="Document deleted.",
        detail=(
            "The database record was removed (dependent rows cascade). Stored "
            "files are cleaned up when ingestion lands in Phase 2."
        ),
    )


@router.post("/{document_id}/reindex")
async def reindex_document(
    document_id: uuid.UUID, session: DbSession, current_user: CurrentUser
) -> None:
    document_service = DocumentService(session)
    if (
        await document_service.get(
            organization_id=current_user.organization_id, document_id=document_id
        )
        is None
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Reindexing is planned for Phase 2 (parsing, embeddings, Qdrant indexing).",
    )