import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class Account(SQLModel, table=True):
	"""Modelo de dominio para Account.

	Campos:
	- id: UUID primario
	- user_id: FK hacia User.id
	- email: opcional (útil si se busca por email desde repositorio/service)
	- account_type_id: tipo de cuenta (int)
	- account_status_type_id: estado de la cuenta (1=active por defecto)
	- created_at, updated_at: timestamps UTC
	"""

	id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
	user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
	email: Optional[str] = Field(default=None, index=True)
	account_type_id: int
	account_status_type_id: int = Field(default=1)
	created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
	updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)}
		)
