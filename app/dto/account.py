from pydantic import BaseModel, constr

from app.domain.models.account import AccountType


class CreateAccountDto(BaseModel):
    name: constr(min_length=1, strip_whitespace=True)  # type: ignore[valid-type]
    account_type: AccountType


class UpdateAccountDto(BaseModel):
    name: constr(min_length=1, strip_whitespace=True) | None = None  # type: ignore[valid-type]
