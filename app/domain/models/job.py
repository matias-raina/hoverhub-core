import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel, CheckConstraint

from app.domain.models.fields import created_at_field, updated_at_field

if TYPE_CHECKING:
    from app.domain.models.account import Account
    from app.domain.models.application import Application
    from app.domain.models.favorite import Favorite


class Job(SQLModel, table=True):
    """Job model."""

    __table_args__ = (
        CheckConstraint("budget >= 0", name="chk_budget_non_negative"),
        CheckConstraint("end_date >= start_date", name="chk_end_date_after_start_date"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
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
    applications: list["Application"] = Relationship(back_populates="job")
    favorites: list["Favorite"] = Relationship(back_populates="job")


class JobUpdate(SQLModel):
    """Job update model."""

    __table_args__ = (
        CheckConstraint("budget >= 0", name="chk_budget_non_negative"),
        CheckConstraint("end_date >= start_date", name="chk_end_date_after_start_date"),
    )

    title: str | None = None
    description: str | None = None
    budget: float | None = None
    location: str | None = None
    start_date: date | None = None
    end_date: date | None = None
