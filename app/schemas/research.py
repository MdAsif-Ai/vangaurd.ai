"""Research and evidence API schemas."""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ResearchCreate(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    mode: Literal["fast", "deep"] = "fast"


class ResearchJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    question: str
    status: str
    mode: str
    result: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime


class ResearchStatusResponse(BaseModel):
    id: uuid.UUID
    status: str


class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    claim_id: uuid.UUID
    document_id: uuid.UUID | None
    chunk_id: str | None
    source_type: str
    page: int | None
    passage: str
    support_status: str
    created_at: datetime


class EvidenceListResponse(BaseModel):
    items: list[EvidenceResponse]