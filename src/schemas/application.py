from pydantic import BaseModel
from typing import List


class ApplicationCreate(BaseModel):
    job_id: int
    user_id: int
    status: str


class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    user_id: int
    status: str

    class Config:
        orm_mode = True


class ApplicationListResponse(BaseModel):
    applications: List[ApplicationResponse]
