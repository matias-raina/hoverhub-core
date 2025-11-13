from app.domain.repositories.interfaces.account import IAccountRepository
from app.domain.repositories.interfaces.application import IApplicationRepository
from app.domain.repositories.interfaces.auth import IAuthRepository
from app.domain.repositories.interfaces.favorite import IFavoriteRepository
from app.domain.repositories.interfaces.job import IJobRepository
from app.domain.repositories.interfaces.session import ISessionRepository
from app.domain.repositories.interfaces.user import IUserRepository

__all__ = [
    "IUserRepository",
    "IAuthRepository",
    "IJobRepository",
    "IAccountRepository",
    "ISessionRepository",
    "IFavoriteRepository",
    "IApplicationRepository",
]
