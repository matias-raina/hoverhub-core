import uuid

from pydantic import BaseModel


class CreateFavoriteDto(BaseModel):
    job_id: uuid.UUID
