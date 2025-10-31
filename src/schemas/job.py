from pydantic import BaseModel


class JobBase(BaseModel):
    title: str
    description: str


class JobCreate(JobBase):
    pass


class JobResponse(JobBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
