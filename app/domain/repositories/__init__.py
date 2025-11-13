from app.domain.repositories.account import AccountRepository
from app.domain.repositories.application import ApplicationRepository
from app.domain.repositories.auth import AuthRepository
from app.domain.repositories.favorite import FavoriteRepository
from app.domain.repositories.job import JobRepository
from app.domain.repositories.session import SessionRepository
from app.domain.repositories.user import UserRepository

__all__ = [
    "UserRepository",
    "AuthRepository",
    "JobRepository",
    "AccountRepository",
    "SessionRepository",
    "FavoriteRepository",
    "ApplicationRepository",
]
