# File: /hoverhub-backend/hoverhub-backend/src/api/__init__.py

from fastapi import APIRouter
from .routes.auth import AuthRouter
from .routes.users import UserRouter
from .routes.jobs import JobRouter
from .routes.applications import ApplicationRouter
from .routes.favorites import FavoriteRouter

api_router = APIRouter()

# Include all the routers
api_router.include_router(AuthRouter().router, prefix="/auth", tags=["auth"])
api_router.include_router(UserRouter().router, prefix="/users", tags=["users"])
api_router.include_router(JobRouter().router, prefix="/jobs", tags=["jobs"])
api_router.include_router(ApplicationRouter().router, prefix="/applications", tags=["applications"])
api_router.include_router(FavoriteRouter().router, prefix="/favorites", tags=["favorites"])