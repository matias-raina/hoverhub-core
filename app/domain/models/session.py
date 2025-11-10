import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, cast

from sqlmodel import Field, Relationship, SQLModel

from app.domain.models.fields import CreatedAtField, UpdatedAtField

if TYPE_CHECKING:
    from app.domain.models.user import User


class UserSession(SQLModel, table=True):
    __tablename__ = "session"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    host: str
    is_active: bool = Field(default=True)
    expires_at: datetime = Field(index=True)
    created_at: datetime = CreatedAtField()
    updated_at: datetime = UpdatedAtField()

    user: "User" = Relationship(back_populates="sessions")

    def is_expired(self) -> bool:
        """Check if the session has expired."""
        now = datetime.now(timezone.utc)
        # At runtime, expires_at is always a datetime instance
        expires_at_dt = cast(datetime, self.expires_at)

        # Ensure expires_at is timezone-aware for comparison
        if expires_at_dt.tzinfo is None:  # type: ignore[attr-defined]
            expires_at_dt = expires_at_dt.replace(tzinfo=timezone.utc)  # type: ignore[attr-defined]

        return now >= expires_at_dt
