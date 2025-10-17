from pydantic import BaseModel
from typing import List


class FavoriteBase(BaseModel):
    job_id: int


class FavoriteCreate(FavoriteBase):
    pass


class FavoriteResponse(FavoriteBase):
    id: int

    class Config:
        orm_mode = True


class FavoritesList(BaseModel):
    favorites: List[FavoriteResponse]
