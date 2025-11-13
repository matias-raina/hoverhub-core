from pydantic import BaseModel

from app.domain.models.application import ApplicationStatus


class CreateApplicationDto(BaseModel):
    message: str | None = None


class UpdateApplicationStatusDto(BaseModel):
    status: ApplicationStatus
    message: str | None = None
