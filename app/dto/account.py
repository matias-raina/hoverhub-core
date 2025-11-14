from typing import Annotated

from pydantic import BaseModel, StringConstraints

from app.domain.models.account import AccountType


class CreateAccountDto(BaseModel):
    name: Annotated[str, StringConstraints(min_length=3, strip_whitespace=True)]
    account_type: AccountType


class UpdateAccountDto(BaseModel):
    name: Annotated[str, StringConstraints(min_length=3, strip_whitespace=True)] | None = None
