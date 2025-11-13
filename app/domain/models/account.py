import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Column, Enum, Field, Relationship, SQLModel

from app.domain.models.fields import created_at_field, updated_at_field

if TYPE_CHECKING:
    from app.domain.models.application import Application
    from app.domain.models.favorite import Favorite
    from app.domain.models.job import Job
    from app.domain.models.user import User


class AccountType(str, enum.Enum):
    """Account type enum."""

    DRONER = "DRONER"
    EMPLOYER = "EMPLOYER"


class Account(SQLModel, table=True):
    """Account model."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    name: str = Field(nullable=False)
    account_type: AccountType = Field(sa_column=Column(Enum(AccountType)))
    is_active: bool = Field(default=True)
    created_at: datetime = created_at_field()
    updated_at: datetime = updated_at_field()

    user: "User" = Relationship(back_populates="account")
    applications: list["Application"] = Relationship(back_populates="account")
    favorites: list["Favorite"] = Relationship(back_populates="account")
    jobs: list["Job"] = Relationship(back_populates="account")


class AccountUpdate(SQLModel):
    """Account update model."""

    name: str | None = None
