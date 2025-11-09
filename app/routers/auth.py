from fastapi import APIRouter, status

from app.config.dependencies import AuthenticatedUserDep, AuthServiceDep
from app.dto.auth import SigninDTO, SignupDTO

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(dto: SignupDTO, auth_service: AuthServiceDep):
    """
    Register a new user account.

    Args:
        dto: Signup data containing email and password
        auth_service: Injected authentication service

    Returns:
        User information and success message
    """
    user = auth_service.signup(dto)
    return {
        "message": "User registered successfully",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "created_at": user.created_at.isoformat(),
        },
    }


@router.post("/signin")
async def signin(dto: SigninDTO, auth_service: AuthServiceDep):
    """
    Sign in with email and password (JSON format).

    Returns a JWT access token that should be included in subsequent requests
    as: Authorization: Bearer <token>

    Args:
        dto: Signin credentials (email and password)
        auth_service: Injected authentication service

    Returns:
        Access token and token type
    """
    access_token = auth_service.signin(dto)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/signout")
async def signout():
    """
    Sign out endpoint (JWT tokens are stateless).

    Client should discard the token on their side.
    For proper logout, implement token blacklisting or use short-lived tokens.

    Returns:
        Success message
    """
    return {"message": "Successfully signed out. Please discard your access token."}


@router.get("/me")
async def get_authenticated_user(authenticated_user: AuthenticatedUserDep):
    """
    Get currently authenticated user information.

    Requires a valid JWT token in the Authorization header.

    Args:
        authenticated_user: Current authenticated user (injected from JWT)

    Returns:
        Current user information
    """
    return {
        "id": str(authenticated_user.id),
        "email": authenticated_user.email,
        "is_active": authenticated_user.is_active,
        "created_at": authenticated_user.created_at.isoformat(),
        "updated_at": authenticated_user.updated_at.isoformat(),
    }
