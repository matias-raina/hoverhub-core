import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Column, Enum, Field, Relationship, SQLModel

from app.domain.models.fields import created_at_field, updated_at_field

if TYPE_CHECKING:
    from app.domain.models.account import Account
    from app.domain.models.job import Job


class ApplicationStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


class Application(SQLModel, table=True):
    """Application model: a Droner applies to a Job posted by an Account."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    job_id: uuid.UUID = Field(foreign_key="job.id", index=True)
    account_id: uuid.UUID = Field(foreign_key="account.id", index=True)
    message: Optional[str] = None
    status: ApplicationStatus = Field(
        sa_column=Column(Enum(ApplicationStatus)), default=ApplicationStatus.PENDING
    )
    created_at: datetime = created_at_field()
    updated_at: datetime = updated_at_field()

    # Relationships (back_populates can be added on the other side later)
    job: "Job" = Relationship(back_populates="applications")
    account: "Account" = Relationship(back_populates="applications")


class ApplicationCreate(SQLModel):
    message: Optional[str] = None


class ApplicationUpdate(SQLModel):
    status: Optional[ApplicationStatus] = None
    message: Optional[str] = None
