from typing import Optional

from pydantic import BaseModel

from app.domain.models.application import ApplicationStatus


class CreateApplicationDto(BaseModel):
    message: Optional[str] = None


class UpdateApplicationStatusDto(BaseModel):
    status: ApplicationStatus
    message: Optional[str] = None
