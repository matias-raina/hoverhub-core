import enum
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Tuple, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class JwtTokenType(str, enum.Enum):
    """Token type enum."""

    ACCESS = "access"
    REFRESH = "refresh"


class JwtTokenPayload(BaseModel):
    """Token payload model with automatic UUID conversion."""

    model_config = ConfigDict(use_enum_values=True)

    sub: UUID
    sid: UUID
    type: JwtTokenType
    iat: Union[datetime, int]  # JWT returns int timestamps
    exp: Union[datetime, int]  # JWT returns int timestamps
    jti: str

    @field_validator("sub", "sid", mode="before")
    @classmethod
    def convert_to_uuid(cls, v):
        """Convert string UUIDs to UUID objects."""
        if isinstance(v, UUID):
            return v
        if isinstance(v, str):
            return UUID(v)
        return v

    @property
    def exp_timestamp(self) -> int:
        """Get expiration as Unix timestamp."""
        if isinstance(self.exp, datetime):
            return int(self.exp.timestamp())
        return self.exp

    @property
    def iat_timestamp(self) -> int:
        """Get issued at as Unix timestamp."""
        if isinstance(self.iat, datetime):
            return int(self.iat.timestamp())
        return self.iat


class IAuthRepository(ABC):
    """Auth repository interface."""

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password."""

    @abstractmethod
    def hash_password(self, plain_password: str) -> str:
        """Hash a plain text password."""

    @abstractmethod
    def decode_token(self, token: str) -> dict:
        """Decode a token and return raw payload dictionary."""

    @abstractmethod
    def create_token(self, data: dict) -> Tuple[str, str, datetime]:
        """Create access and refresh tokens for a user. Returns a tuple of (access_token, refresh_token, refresh_token_exp)."""
