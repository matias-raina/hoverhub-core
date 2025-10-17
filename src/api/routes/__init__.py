# File: /hoverhub-backend/hoverhub-backend/src/api/routes/__init__.py

from fastapi import APIRouter
from .auth import AuthRouter
from .users import UserRouter
from .jobs import JobRouter
from .applications import ApplicationRouter
from .favorites import FavoriteRouter

router = APIRouter()

# Include all the routers
router.include_router(AuthRouter().router, prefix="/auth", tags=["auth"])
router.include_router(UserRouter().router, prefix="/users", tags=["users"])
router.include_router(JobRouter().router, prefix="/jobs", tags=["jobs"])
router.include_router(ApplicationRouter().router, prefix="/applications", tags=["applications"])
router.include_router(FavoriteRouter().router, prefix="/favorites", tags=["favorites"])