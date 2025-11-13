from typing import Annotated

from pydantic import BaseModel, EmailStr, StringConstraints


class SignupDTO(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8)]


class SigninDTO(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8)]
