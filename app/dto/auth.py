from pydantic import BaseModel, EmailStr, constr


class SignupDTO(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class SigninDTO(BaseModel):
    email: EmailStr
    password: constr(min_length=8)
