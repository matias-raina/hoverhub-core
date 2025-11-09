from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.config.database import get_db
from app.config.settings import Settings, get_settings
from app.domain.models.user import User
from app.domain.repositories.account import AccountRepository
from app.domain.repositories.auth import AuthRepository
from app.domain.repositories.interfaces.account import IAccountRepository
from app.domain.repositories.interfaces.auth import IAuthRepository
from app.domain.repositories.interfaces.job import IJobRepository
from app.domain.repositories.interfaces.user import IUserRepository
from app.domain.repositories.job import JobRepository
from app.domain.repositories.user import UserRepository
from app.services.account import AccountService
from app.services.auth import AuthService
from app.services.interfaces.account import IAccountService
from app.services.interfaces.auth import IAuthService
from app.services.interfaces.job import IJobService
from app.services.interfaces.user import IUserService
from app.services.job import JobService
from app.services.user import UserService

# HTTP Bearer scheme for token authentication
http_bearer = HTTPBearer()

# Database dependency
SessionDep = Annotated[Session, Depends(get_db)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


# Repository dependencies
def get_user_repository(
    session: SessionDep,
) -> IUserRepository:
    return UserRepository(session)


def get_auth_repository(
    settings: SettingsDep,
) -> IAuthRepository:
    return AuthRepository(settings)


def get_job_repository(
    session: SessionDep,
) -> IJobRepository:
    return JobRepository(session)


def get_account_repository(
    session: SessionDep,
) -> IAccountRepository:
    return AccountRepository(session)


UserRepositoryDep = Annotated[IUserRepository, Depends(get_user_repository)]
AuthRepositoryDep = Annotated[IAuthRepository, Depends(get_auth_repository)]
JobRepositoryDep = Annotated[IJobRepository, Depends(get_job_repository)]
AccountRepositoryDep = Annotated[IAccountRepository, Depends(get_account_repository)]


# Service dependencies
def get_auth_service(
    auth_repository: AuthRepositoryDep,
    user_repository: UserRepositoryDep,
) -> IAuthService:
    return AuthService(auth_repository, user_repository)


def get_user_service(
    user_repository: UserRepositoryDep,
) -> IUserService:
    return UserService(user_repository)


def get_job_service(
    job_repository: JobRepositoryDep,
) -> IJobService:
    return JobService(job_repository)


def get_account_service(
    account_repository: AccountRepositoryDep,
    user_repository: UserRepositoryDep,
) -> IAccountService:
    return AccountService(account_repository, user_repository)


AuthServiceDep = Annotated[IAuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[IUserService, Depends(get_user_service)]
JobServiceDep = Annotated[IJobService, Depends(get_job_service)]
AccountServiceDep = Annotated[IAccountService, Depends(get_account_service)]


# Authentication dependency - Gets authenticated user from JWT token
def get_authenticated_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
    auth_service: AuthServiceDep,
) -> User:
    return auth_service.get_authenticated_user(credentials.credentials)


AuthenticatedUserDep = Annotated[User, Depends(get_authenticated_user)]
