from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.client import Redis
from sqlmodel import Session

from app.config import Settings, get_cache, get_db, get_settings
from app.domain.models.account import Account
from app.domain.models.user import User
from app.domain.repositories import (
    AccountRepository,
    ApplicationRepository,
    AuthRepository,
    JobRepository,
    SessionRepository,
    UserRepository,
    FavoriteRepository,
)
from app.domain.repositories.interfaces import (
    IAccountRepository,
    IApplicationRepository,
    IAuthRepository,
    IJobRepository,
    ISessionRepository,
    IUserRepository,
    IFavoriteRepository,
)
from app.services import AccountService, ApplicationService, AuthService, JobService, UserService, FavoriteService
from app.services.interfaces import (
    IAccountService,
    IApplicationService,
    IAuthService,
    IJobService,
    IUserService,
    IFavoriteService,
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


def get_favorite_repository(
    session: SessionDep,
) -> IFavoriteRepository:
    """Get the favorite repository."""
    return FavoriteRepository(session)


def get_application_repository(
    session: SessionDep,
) -> IApplicationRepository:
    """Get the application repository."""
    return ApplicationRepository(session)


UserRepositoryDep = Annotated[IUserRepository, Depends(get_user_repository)]
AuthRepositoryDep = Annotated[IAuthRepository, Depends(get_auth_repository)]
JobRepositoryDep = Annotated[IJobRepository, Depends(get_job_repository)]
FavoriteRepositoryDep = Annotated[IFavoriteRepository, Depends(get_favorite_repository)]
AccountRepositoryDep = Annotated[IAccountRepository, Depends(get_account_repository)]
SessionRepositoryDep = Annotated[ISessionRepository, Depends(get_session_repository)]
ApplicationRepositoryDep = Annotated[IApplicationRepository, Depends(get_application_repository)]


# Service dependencies
def get_auth_service(
    cache: CacheDep,
    auth_repository: AuthRepositoryDep,
    user_repository: UserRepositoryDep,
    session_repository: SessionRepositoryDep,
    account_repository: AccountRepositoryDep,
) -> IAuthService:
    """Get the auth service."""
    return AuthService(
        cache,
        auth_repository,
        user_repository,
        session_repository,
        account_repository,
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


def get_favorite_service(
    favorite_repository: FavoriteRepositoryDep,
) -> IFavoriteService:
    """Get the favorite service."""
    return FavoriteService(favorite_repository)
  
  
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


AuthServiceDep = Annotated[IAuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[IUserService, Depends(get_user_service)]
JobServiceDep = Annotated[IJobService, Depends(get_job_service)]
AccountServiceDep = Annotated[IAccountService, Depends(get_account_service)]
FavoriteServiceDep = Annotated[IFavoriteService, Depends(get_favorite_service)]
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


def get_account_context(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
    auth_service: Annotated[IAuthService, Depends(get_auth_service)],
    x_account_id: str = Header(..., alias="x-account-id"),
) -> Account:
    """
    Get and validate account context from x-account-id header.

    Ensures the authenticated user owns the specified account.
    """
    try:
        account_id = UUID(x_account_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid account ID format",
        ) from exc

    # This will validate authentication and ownership
    return auth_service.get_authenticated_account(credentials.credentials, account_id)


AuthenticatedUserDep = Annotated[User, Depends(get_authenticated_user)]
AuthTokenDep = Annotated[str, Depends(get_auth_token)]
AccountContextDep = Annotated[Account, Depends(get_account_context)]
