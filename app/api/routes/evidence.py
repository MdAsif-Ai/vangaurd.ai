"""Evidence API. Returns real (currently empty) organization-scoped results."""

import uuid

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import CurrentUser, DbSession
from app.schemas.research import EvidenceListResponse, EvidenceResponse
from app.services.evidence import EvidenceService

router = APIRouter()


@router.get("/research/{research_job_id}/evidence", response_model=EvidenceListResponse)
async def list_research_evidence(
    research_job_id: uuid.UUID, session: DbSession, current_user: CurrentUser
) -> EvidenceListResponse:
    """List evidence attached to a research job's claims (empty for now)."""
    evidence = await EvidenceService(session).list_for_job(
        organization_id=current_user.organization_id, research_job_id=research_job_id
    )
    if evidence is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Research job not found"
        )
    return EvidenceListResponse(
        items=[EvidenceResponse.model_validate(item) for item in evidence]
    )


@router.get("/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(
    evidence_id: uuid.UUID, session: DbSession, current_user: CurrentUser
) -> EvidenceResponse:
    evidence = await EvidenceService(session).get(
        organization_id=current_user.organization_id, evidence_id=evidence_id
    )
    if evidence is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found")
    return EvidenceResponse.model_validate(evidence)