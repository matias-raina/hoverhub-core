from app.services.interfaces.account import IAccountService
from app.services.interfaces.application import IApplicationService
from app.services.interfaces.auth import IAuthService
from app.services.interfaces.job import IJobService
from app.services.interfaces.user import IUserService
from app.services.interfaces.favorite import IFavoriteService

__all__ = [
    "IAccountService",
    "IAuthService",
    "IJobService",
    "IUserService",
    "IApplicationService",
    "IFavoriteService"
]
