import enum
import uuid
from datetime import datetime

from sqlmodel import Column, Enum, Field, SQLModel

from app.domain.models.fields import CreatedAtField, UpdatedAtField


class AccountType(str, enum.Enum):
    DRONER = "DRONER"
    EMPLOYER = "EMPLOYER"


class Account(SQLModel, table=True):

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    name: str = Field(nullable=False)
    account_type: AccountType = Field(sa_column=Column(Enum(AccountType)))
    is_active: bool = Field(default=True)
    created_at: datetime = CreatedAtField()
    updated_at: datetime = UpdatedAtField()
