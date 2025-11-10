from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.domain.models.application import ApplicationStatus


class CreateApplicationDto(BaseModel):
    message: Optional[str] = None


class UpdateApplicationStatusDto(BaseModel):
    status: ApplicationStatus
    message: Optional[str] = None


class ApplicationDto(BaseModel):
    id: UUID
    job_id: UUID
    account_id: UUID
    status: ApplicationStatus
    message: Optional[str]
    created_at: str
    updated_at: str
