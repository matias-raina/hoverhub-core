from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.domain.models.user import User
from app.domain.repositories.interfaces.auth import IAuthRepository
from app.domain.repositories.interfaces.user import IUserRepository
from app.dto.auth import SigninDTO, SignupDTO
from app.services.interfaces.auth import IAuthService


class AuthService(IAuthService):
    def __init__(
        self, auth_repository: IAuthRepository, user_repository: IUserRepository
    ):
        self.auth_repository = auth_repository
        self.user_repository = user_repository

    def signup(self, dto: SignupDTO) -> User:
        """Register a new user."""
        hashed_password = self.auth_repository.hash_password(dto.password)

        user = User(email=dto.email, hashed_password=hashed_password)

        try:
            user = self.user_repository.create(user)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            ) from exc

        return user

    def signin(self, dto: SigninDTO) -> str:
        """Authenticate a user and return JWT access token."""
        user = self.user_repository.get_by_email(dto.email)

        if not user or not self.auth_repository.verify_password(
            dto.password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return self.auth_repository.create_token(
            {"sub": str(user.id), "email": user.email}
        )

    def authorize(self, token: str) -> dict:
        """Authorize a user by token."""
        return self.auth_repository.verify_token(token)

    def get_authenticated_user(self, token: str) -> User:
        try:
            payload = self.authorize(token)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        # Extract user ID from token payload
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Fetch user from database
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user account is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user account",
            )

        return user

    def signout(self):
        """Sign out a user."""
        return {"message": "Successfully signed out"}
