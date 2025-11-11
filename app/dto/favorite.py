from pydantic import BaseModel

import uuid


class CreateFavoriteDto(BaseModel):
    job_id: uuid.UUID
