from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.config.database import get_db
from app.config.settings import Settings, get_settings
from app.domain.models.user import User
from app.domain.repositories.auth import AuthRepository
from app.domain.repositories.interfaces.auth import IAuthRepository
from app.domain.repositories.interfaces.user import IUserRepository
from app.domain.repositories.user import UserRepository
from app.services.auth import AuthService
from app.services.interfaces.auth import IAuthService
from app.services.interfaces.user import IUserService
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


UserRepositoryDep = Annotated[IUserRepository, Depends(get_user_repository)]
AuthRepositoryDep = Annotated[IAuthRepository, Depends(get_auth_repository)]


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


AuthServiceDep = Annotated[IAuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[IUserService, Depends(get_user_service)]


# Authentication dependency - Gets current user from JWT token
def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
    auth_repository: AuthRepositoryDep,
    user_repository: UserRepositoryDep,
) -> User:
    """
    Extract and validate JWT token using HTTPBearer, return current user.

    The token is automatically extracted from the Authorization header by FastAPI.
    Expects header: Authorization: Bearer <token>

    Args:
        credentials: HTTP Bearer credentials containing the JWT token
        auth_repository: Authentication repository for token validation
        user_repository: User repository to fetch user data

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Verify token and extract payload (now with better error handling)
    try:
        payload = auth_repository.verify_token(credentials.credentials)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user_id = payload.get("sub")

    user = user_repository.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
