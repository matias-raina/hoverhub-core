from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.schemas.user import UserCreate, UserResponse
from src.services.user_service import UserService
from src.config.database import get_db
from src.repositories.user_repository import UserRepository


class UserRouter:
    def __init__(self):
        self.router = APIRouter()
        self.user_service = UserService(UserRepository(Depends(get_db)))

        self.router.add_api_route(
            "/users", self.create_user, methods=["POST"], response_model=UserResponse)
        self.router.add_api_route(
            "/users/{user_id}", self.get_user, methods=["GET"], response_model=UserResponse)
        self.router.add_api_route(
            "/users/{user_id}", self.update_user, methods=["PUT"], response_model=UserResponse)
        self.router.add_api_route(
            "/users/{user_id}", self.delete_user, methods=["DELETE"])

    async def create_user(self, user: UserCreate, db: Session = Depends(get_db)):
        return await self.user_service.create_user(user, db)

    async def get_user(self, user_id: int, db: Session = Depends(get_db)):
        user = await self.user_service.get_user_by_id(user_id, db)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def update_user(self, user_id: int, user: UserCreate, db: Session = Depends(get_db)):
        updated_user = await self.user_service.update_user(user_id, user, db)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user

    async def delete_user(self, user_id: int, db: Session = Depends(get_db)):
        result = await self.user_service.delete_user(user_id, db)
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return {"detail": "User deleted successfully"}


user_router = UserRouter().router
