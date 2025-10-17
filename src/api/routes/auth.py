from fastapi import APIRouter, HTTPException
from src.schemas.user import UserCreate, UserResponse
from src.services.auth_service import AuthService


class AuthRouter:
    def __init__(self):
        self.router = APIRouter()
        self.auth_service = AuthService()
        self.setup_routes()

    def setup_routes(self):
        self.router.post(
            "/login", response_model=UserResponse)(self.login_user)
        self.router.post(
            "/register", response_model=UserResponse)(self.register_user)

    async def login_user(self, username: str, password: str):
        user = await self.auth_service.authenticate_user(username, password)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid credentials")
        return user

    async def register_user(self, user_create: UserCreate):
        user = await self.auth_service.create_user(user_create)
        return user


auth_router = AuthRouter().router
