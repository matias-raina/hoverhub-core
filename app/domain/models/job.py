import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.domain.models.fields import CreatedAtField, UpdatedAtField

if TYPE_CHECKING:
    from app.domain.models.account import Account


class Job(SQLModel, table=True):

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    account_id: uuid.UUID = Field(foreign_key="account.id", index=True)
    title: str
    description: str
    budget: float
    location: str
    start_date: date
    end_date: date
    created_at: datetime = CreatedAtField()
    updated_at: datetime = UpdatedAtField()

    account: "Account" = Relationship(back_populates="jobs")


class JobUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    budget: Optional[float] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
