import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from app.domain.models.fields import CreatedAtField, UpdatedAtField


class User(SQLModel, table=True):

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = CreatedAtField()
    updated_at: datetime = UpdatedAtField()
