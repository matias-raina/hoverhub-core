from fastapi import APIRouter, HTTPException
from src.schemas.user import UserCreate, UserResponse
from src.services.auth_service import AuthService


class AuthRouter:
    def __init__(self):
        self.router = APIRouter()
        self.auth_service = AuthService()

        self.router.add_api_route(
            "/login", self.login_user, methods=["POST"], response_model=UserResponse)
        self.router.add_api_route(
            "/logout", self.logout_user, methods=["POST"], response_model=UserResponse)
        self.router.add_api_route(
            "/register", self.register_user, methods=["POST"], response_model=UserResponse)

    async def login_user(self, username: str, password: str):
        user = await self.auth_service.authenticate_user(username, password)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid credentials")
        return user

    async def logout_user(self, user_id: int):
        user = await self.auth_service.logout_user(user_id)
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        return user

    async def register_user(self, user_create: UserCreate):
        user = await self.auth_service.create_user(user_create)
        return user


auth_router = AuthRouter().router
