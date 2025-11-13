from typing import Optional, Annotated

from pydantic import BaseModel, StringConstraints

from app.domain.models.account import AccountType


class CreateAccountDto(BaseModel):
    name: Annotated[str, StringConstraints(
        min_length=1, strip_whitespace=True)]
    account_type: AccountType


class UpdateAccountDto(BaseModel):
    name: Optional[Annotated[str, StringConstraints(
        min_length=1, strip_whitespace=True)]] = None
