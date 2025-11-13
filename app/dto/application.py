from typing import Annotated

from pydantic import BaseModel, StringConstraints

from app.domain.models.application import ApplicationStatus


class CreateApplicationDto(BaseModel):
    message: Annotated[str, StringConstraints(max_length=500)] | None = None


class UpdateApplicationStatusDto(BaseModel):
    status: ApplicationStatus
    message: Annotated[str, StringConstraints(max_length=500)] | None = None
