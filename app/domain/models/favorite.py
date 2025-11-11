import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.domain.models.fields import created_at_field

if TYPE_CHECKING:
    from app.domain.models.job import Job
    from app.domain.models.account import Account


class Favorite(SQLModel, table=True):
    """Favorite model."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4,
                          primary_key=True, index=True)
    job_id: uuid.UUID = Field(foreign_key="job.id", index=True)
    account_id: uuid.UUID = Field(foreign_key="account.id", index=True)
    created_at: datetime = created_at_field()

    job: "Job" = Relationship(back_populates="favorites")
    account: "Account" = Relationship(back_populates="favorites")
