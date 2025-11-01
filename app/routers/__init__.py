from app.routers.auth import router as auth_router
from app.routers.users import router as users_router

routers = [auth_router, users_router]
