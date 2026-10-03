"""Evidence API: single evidence lookup, organization-scoped.

The research-job evidence listing lives in routes/research.py under
/api/research/{job_id}/evidence. Keeping this router under its own
/evidence prefix avoids a catch-all route at the API root, so unknown
paths correctly return 404.
"""

import uuid

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import CurrentUser, DbSession
from app.schemas.research import EvidenceResponse
from app.services.evidence import EvidenceService

router = APIRouter()


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
