from app.domain.repositories.interfaces.auth import IAuthRepository
from app.domain.repositories.interfaces.user import IUserRepository
from app.domain.repositories.interfaces.job import IJobRepository
from app.domain.repositories.interfaces.account import IAccountRepository

__all__ = ["IUserRepository", "IAuthRepository",
           "IJobRepository", "IAccountRepository"]
