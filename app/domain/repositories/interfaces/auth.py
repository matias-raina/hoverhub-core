from abc import ABC, abstractmethod
from datetime import datetime
from typing import Tuple
from uuid import UUID


class IAuthRepository(ABC):
    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password."""

    @abstractmethod
    def hash_password(self, plain_password: str) -> str:
        """Hash a plain text password."""

    @abstractmethod
    def decode_token(self, token: str) -> dict:
        """Decode a token and return payload."""

    @abstractmethod
    def create_token(
        self, data: dict
    ) -> Tuple[UUID, str, datetime, UUID, str, datetime]:
        """Create access and refresh tokens for a user."""
