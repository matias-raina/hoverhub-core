from typing import Optional, Annotated

from pydantic import BaseModel, StringConstraints

from app.domain.models.application import ApplicationStatus


class CreateApplicationDto(BaseModel):
    message: Optional[Annotated[str, StringConstraints(max_length=500)]] = None


class UpdateApplicationStatusDto(BaseModel):
    status: ApplicationStatus
    message: Optional[Annotated[str, StringConstraints(max_length=500)]] = None
