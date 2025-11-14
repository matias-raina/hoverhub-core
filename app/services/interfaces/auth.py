from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models.account import Account
from app.domain.models.user import User
from app.domain.repositories.interfaces.auth import JwtTokenPayload
from app.dto.auth import SigninDTO, SignupDTO


class IAuthService(ABC):
    """Auth service interface."""

    @abstractmethod
    def signup(self, client_ip: str, dto: SignupDTO) -> tuple[User, str, str]:
        """Register a new user."""

    @abstractmethod
    def signin(self, client_ip: str, dto: SigninDTO) -> tuple[str, str]:
        """Authenticate a user and return JWT access token and refresh token."""

    @abstractmethod
    def authorize(self, token: str) -> JwtTokenPayload:
        """Authorize a user by token and return token payload."""

    @abstractmethod
    def get_authenticated_user(self, token: str) -> User:
        """Get authenticated user from access token."""

    @abstractmethod
    def get_authenticated_account(self, token: str, account_id: UUID) -> Account:
        """Get authenticated account from access token and account ID."""

    @abstractmethod
    def refresh_token(self, refresh_token: str) -> tuple[str, str]:
        """Refresh access token using refresh token."""

    @abstractmethod
    def signout(self, token: str) -> bool:
        """Sign out a user and revoke their session."""
