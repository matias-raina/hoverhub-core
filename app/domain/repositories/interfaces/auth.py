import enum
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Tuple, TypedDict


class JwtTokenType(str, enum.Enum):
    """Token type enum."""

    ACCESS = "access"
    REFRESH = "refresh"


class JwtTokenPayload(TypedDict):
    """Token payload type."""

    sub: str
    sid: str
    type: JwtTokenType
    iat: datetime
    exp: datetime
    jti: str


class IAuthRepository(ABC):
    """Auth repository interface."""

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password."""

    @abstractmethod
    def hash_password(self, plain_password: str) -> str:
        """Hash a plain text password."""

    @abstractmethod
    def decode_token(self, token: str) -> JwtTokenPayload:
        """Decode a token and return payload."""

    @abstractmethod
    def create_token(self, data: dict) -> Tuple[str, str, datetime]:
        """Create access and refresh tokens for a user. Returns a tuple of (access_token, refresh_token, refresh_token_exp)."""
