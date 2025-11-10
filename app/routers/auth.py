from fastapi import APIRouter, Request, status
from pydantic import BaseModel

from app.config.dependencies import AuthenticatedUserDep, AuthServiceDep, AuthTokenDep
from app.dto.auth import SigninDTO, SignupDTO

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(request: Request, dto: SignupDTO, auth_service: AuthServiceDep):
    """
    Register a new user account.

    Args:
        dto: Signup data containing email and password
        auth_service: Injected authentication service

    Returns:
        User information and success message
    """
    user, at, rt = auth_service.signup(request.client.host, dto)

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at,
        },
        "access_token": at,
        "refresh_token": rt,
        "token_type": "bearer",
    }


@router.post("/signin")
async def signin(request: Request, dto: SigninDTO, auth_service: AuthServiceDep):
    """
    Sign in with email and password (JSON format).

    Returns JWT access and refresh tokens. The access token should be included
    in subsequent requests as: Authorization: Bearer <token>

    Args:
        dto: Signin credentials (email, password, and host)
        auth_service: Injected authentication service

    Returns:
        Access token, refresh token, and token type
    """
    at, rt = auth_service.signin(request.client.host, dto)
    return {
        "access_token": at,
        "refresh_token": rt,
        "token_type": "bearer",
    }


@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest, auth_service: AuthServiceDep):
    """
    Refresh access token using a valid refresh token.

    Returns new access and refresh tokens. The old refresh token will be invalidated.

    Args:
        request: Request containing the refresh token
        auth_service: Injected authentication service

    Returns:
        New access token, new refresh token, and token type
    """
    at, rt = auth_service.refresh_token(request.refresh_token)
    return {
        "access_token": at,
        "refresh_token": rt,
        "token_type": "bearer",
    }


@router.post("/signout", status_code=status.HTTP_204_NO_CONTENT)
async def signout(
    token: AuthTokenDep,
    auth_service: AuthServiceDep,
):
    """
    Sign out and revoke the current session.

    This will deactivate the session and blacklist the current token.
    All tokens associated with this session will be invalidated.

    Requires a valid JWT token in the Authorization header.

    Args:
        token: JWT token from Authorization header
        auth_service: Injected authentication service

    Returns:
        Success message
    """
    auth_service.signout(token)
