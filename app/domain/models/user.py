import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.domain.models.fields import created_at_field, updated_at_field

if TYPE_CHECKING:
    from app.domain.models.session import UserSession


class User(SQLModel, table=True):
    """User model."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = created_at_field()
    updated_at: datetime = updated_at_field()

    sessions: list["UserSession"] = Relationship(back_populates="user")
