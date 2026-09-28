"""Research job service.

Phase 1: job creation (queued) and status lookup only. The research
orchestration (retrieval, reasoning, verification) arrives in a later
phase; nothing here fabricates answers.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ResearchJob, ResearchMode, ResearchStatus, User
from app.db.repositories import AuditLogRepository, ResearchJobRepository


class ResearchService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._jobs = ResearchJobRepository(session)
        self._audit = AuditLogRepository(session)

    async def create_job(self, *, user: User, question: str, mode: str) -> ResearchJob:
        """Create a research job in the 'queued' state."""
        job = ResearchJob(
            id=uuid.uuid4(),
            organization_id=user.organization_id,
            user_id=user.id,
            question=question,
            status=ResearchStatus.QUEUED,
            mode=ResearchMode(mode),
            result=None,
        )
        await self._jobs.create(job)
        await self._audit.log(
            organization_id=user.organization_id,
            user_id=user.id,
            action="research.created",
            resource_type="research_job",
            resource_id=str(job.id),
            meta={"mode": mode},
        )
        await self._session.commit()
        return job

    async def get_job(
        self, *, organization_id: uuid.UUID, job_id: uuid.UUID
    ) -> ResearchJob | None:
        return await self._jobs.get(organization_id, job_id)