from app.routers.account import router as account_router
from app.routers.applications import router as applications_router
from app.routers.auth import router as auth_router
from app.routers.jobs import router as jobs_router
from app.routers.users import router as users_router
from app.routers.favorites import router as favorites_router

routers = [auth_router, users_router,
           jobs_router, account_router, applications_router, favorites_router]
