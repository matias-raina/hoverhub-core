from pydantic import BaseModel, EmailStr
from pydantic import constr


class SignupDTO(BaseModel):
    email: EmailStr
    password: constr(min_length=8)  # type: ignore[valid-type]


class SigninDTO(BaseModel):
    email: EmailStr
    password: constr(min_length=8)  # type: ignore[valid-type]
