from typing import Optional

import uuid
from datetime import date, datetime, timezone

from sqlmodel import Field, SQLModel


class Job(SQLModel, table=True):

    id: uuid.UUID = Field(default_factory=uuid.uuid4,
                          primary_key=True, index=True)
    account_id: uuid.UUID = Field(foreign_key="account.id", index=True)
    title: str
    description: str
    budget: float
    location: str
    start_date: date
    end_date: date
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)})


class JobUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    budget: Optional[float] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
