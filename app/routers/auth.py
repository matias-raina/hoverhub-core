from fastapi import APIRouter, Request, status
from pydantic import BaseModel

from app.config.dependencies import AuthServiceDep, AuthTokenDep
from app.dto.auth import SigninDTO, SignupDTO

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RefreshTokenRequest(BaseModel):
    refresh_token: str


def get_client_ip(request: Request) -> str:
    """
    Get the real client IP address from the request.

    Checks proxy headers (X-Forwarded-For, X-Real-IP) first, then falls back
    to request.client.host. This ensures we get the actual client IP even when
    behind a proxy or load balancer.

    Args:
        request: FastAPI Request object

    Returns:
        Client IP address as a string, or "unknown" if unavailable
    """
    # Check X-Forwarded-For header (most common proxy header)
    # Format: "client_ip, proxy1_ip, proxy2_ip"
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP (the original client)
        client_ip = forwarded_for.split(",")[0].strip()
        if client_ip:
            return client_ip

    # Check X-Real-IP header (alternative proxy header)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # Fall back to request.client.host (direct connection or no proxy headers)
    if request.client:
        return request.client.host

    return "unknown"


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
    client_ip = get_client_ip(request)
    user, at, rt = auth_service.signup(client_ip, dto)

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
    client_ip = get_client_ip(request)
    at, rt = auth_service.signin(client_ip, dto)
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
