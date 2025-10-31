from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.schemas.favorite import FavoriteCreate, FavoriteResponse
from src.services.favorite_service import FavoriteService
from src.config.database import get_db
from src.repositories.favorite_repository import FavoriteRepository


class FavoriteRouter:
    def __init__(self):
        self.router = APIRouter()
        self.favorite_service = FavoriteService(
            FavoriteRepository(Depends(get_db)))

        self.router.add_api_route(
            "/favorites", self.add_favorite, methods=["POST"], response_model=FavoriteResponse)
        self.router.add_api_route("/favorites", self.get_favorites,
                                  methods=["GET"], response_model=list[FavoriteResponse])

    async def add_favorite(self, favorite: FavoriteCreate, db: Session = Depends(get_db)):
        try:
            return await self.favorite_service.add_favorite(favorite, db)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_favorites(self, db: Session = Depends(get_db)):
        try:
            return await self.favorite_service.get_favorites(db)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


favorite_router = FavoriteRouter().router
