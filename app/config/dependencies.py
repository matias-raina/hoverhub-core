from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.client import Redis
from sqlmodel import Session

from app.config import Settings, get_cache, get_db, get_settings
from app.domain.models.user import User
from app.domain.repositories import (
    AccountRepository,
    AuthRepository,
    JobRepository,
    SessionRepository,
    UserRepository,
    ApplicationRepository,
)
from app.domain.repositories.interfaces import (
    IAccountRepository,
    IAuthRepository,
    IJobRepository,
    ISessionRepository,
    IUserRepository,
    IApplicationRepository,
)
from app.services import AccountService, AuthService, JobService, UserService, ApplicationService
from app.services.interfaces import (
    IAccountService,
    IAuthService,
    IJobService,
    IUserService,
    IApplicationService,
)

# HTTP Bearer scheme for token authentication
http_bearer = HTTPBearer()

# Database dependency
SessionDep = Annotated[Session, Depends(get_db)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
CacheDep = Annotated[Redis, Depends(get_cache)]


# Repository dependencies
def get_user_repository(
    session: SessionDep,
) -> IUserRepository:
    """Get the user repository."""
    return UserRepository(session)


def get_auth_repository(
    settings: SettingsDep,
) -> IAuthRepository:
    """Get the auth repository."""
    return AuthRepository(settings)


def get_job_repository(
    session: SessionDep,
) -> IJobRepository:
    """Get the job repository."""
    return JobRepository(session)


def get_account_repository(
    session: SessionDep,
) -> IAccountRepository:
    """Get the account repository."""
    return AccountRepository(session)


def get_session_repository(
    session: SessionDep,
) -> ISessionRepository:
    """Get the session repository."""
    return SessionRepository(session)


UserRepositoryDep = Annotated[IUserRepository, Depends(get_user_repository)]
AuthRepositoryDep = Annotated[IAuthRepository, Depends(get_auth_repository)]
JobRepositoryDep = Annotated[IJobRepository, Depends(get_job_repository)]
AccountRepositoryDep = Annotated[IAccountRepository, Depends(get_account_repository)]
SessionRepositoryDep = Annotated[ISessionRepository, Depends(get_session_repository)]
def get_application_repository(
    session: SessionDep,
) -> IApplicationRepository:
    """Get the application repository."""
    return ApplicationRepository(session)

ApplicationRepositoryDep = Annotated[IApplicationRepository, Depends(get_application_repository)]


# Service dependencies
def get_auth_service(
    cache: CacheDep,
    auth_repository: AuthRepositoryDep,
    user_repository: UserRepositoryDep,
    session_repository: SessionRepositoryDep,
) -> IAuthService:
    """Get the auth service."""
    return AuthService(
        cache,
        auth_repository,
        user_repository,
        session_repository,
    )


def get_user_service(
    user_repository: UserRepositoryDep,
    session_repository: SessionRepositoryDep,
) -> IUserService:
    """Get the user service."""
    return UserService(user_repository, session_repository)


def get_job_service(
    job_repository: JobRepositoryDep,
) -> IJobService:
    """Get the job service."""
    return JobService(job_repository)


def get_account_service(
    account_repository: AccountRepositoryDep,
    user_repository: UserRepositoryDep,
) -> IAccountService:
    """Get the account service."""
    return AccountService(account_repository, user_repository)


AuthServiceDep = Annotated[IAuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[IUserService, Depends(get_user_service)]
JobServiceDep = Annotated[IJobService, Depends(get_job_service)]
AccountServiceDep = Annotated[IAccountService, Depends(get_account_service)]
def get_application_service(
    application_repository: ApplicationRepositoryDep,
    account_repository: AccountRepositoryDep,
    job_repository: JobRepositoryDep,
) -> IApplicationService:
    """Get the application service."""
    return ApplicationService(
        application_repository,
        account_repository,
        job_repository,
    )

ApplicationServiceDep = Annotated[IApplicationService, Depends(get_application_service)]


# Authentication dependency - Gets authenticated user from JWT token
def get_authenticated_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
    auth_service: AuthServiceDep,
) -> User:
    """Get the authenticated user."""
    return auth_service.get_authenticated_user(credentials.credentials)


def get_auth_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
) -> str:
    """Get the auth token."""
    return credentials.credentials


AuthenticatedUserDep = Annotated[User, Depends(get_authenticated_user)]
AuthTokenDep = Annotated[str, Depends(get_auth_token)]
