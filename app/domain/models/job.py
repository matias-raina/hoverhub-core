import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional, List

from sqlmodel import Field, Relationship, SQLModel

from app.domain.models.fields import created_at_field, updated_at_field

if TYPE_CHECKING:
    from app.domain.models.account import Account
    from app.domain.models.favorite import Favorite
    from app.domain.models.application import Application


class Job(SQLModel, table=True):
    """Job model."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4,
                          primary_key=True, index=True)
    account_id: uuid.UUID = Field(foreign_key="account.id", index=True)
    title: str
    description: str
    budget: float
    location: str
    start_date: date
    end_date: date
    created_at: datetime = created_at_field()
    updated_at: datetime = updated_at_field()

    account: "Account" = Relationship(back_populates="jobs")
    favorites: List["Favorite"] = Relationship(back_populates="job")
    applications: List["Application"] = Relationship(back_populates="job")


class JobUpdate(SQLModel):
    """Job update model."""

    title: Optional[str] = None
    description: Optional[str] = None
    budget: Optional[float] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
