from app.domain.repositories.interfaces.account import IAccountRepository
from app.domain.repositories.interfaces.auth import IAuthRepository
from app.domain.repositories.interfaces.job import IJobRepository
from app.domain.repositories.interfaces.session import ISessionRepository
from app.domain.repositories.interfaces.user import IUserRepository
from app.domain.repositories.interfaces.application import IApplicationRepository

__all__ = [
    "IUserRepository",
    "IAuthRepository",
    "IJobRepository",
    "IAccountRepository",
    "ISessionRepository",
    "IApplicationRepository",
]
