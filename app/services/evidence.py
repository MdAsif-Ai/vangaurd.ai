"""Evidence lookup service (read-only in Phase 1).

Returns real (currently empty) results scoped to the organization; never
fabricates evidence.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Evidence
from app.db.repositories import EvidenceRepository, ResearchJobRepository


class EvidenceService:
    def __init__(self, session: AsyncSession) -> None:
        self._evidence = EvidenceRepository(session)
        self._research = ResearchJobRepository(session)

    async def list_for_job(
        self, *, organization_id: uuid.UUID, research_job_id: uuid.UUID
    ) -> list[Evidence] | None:
        """Return evidence for a job, or None if the job does not exist."""
        job = await self._research.get(organization_id, research_job_id)
        if job is None:
            return None
        return await self._evidence.list_for_job(organization_id, research_job_id)

    async def get(
        self, *, organization_id: uuid.UUID, evidence_id: uuid.UUID
    ) -> Evidence | None:
        return await self._evidence.get(organization_id, evidence_id)