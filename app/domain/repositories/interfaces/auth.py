from abc import ABC, abstractmethod


class IAuthRepository(ABC):
    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password."""

    @abstractmethod
    def hash_password(self, plain_password: str) -> str:
        """Hash a plain text password."""

    @abstractmethod
    def verify_token(self, token: str) -> dict:
        """Verify a token and return payload."""

    @abstractmethod
    def create_token(self, data: dict) -> str:
        """Create a token for a user."""

    @abstractmethod
    def decode_token(self, token: str) -> dict:
        """Decode a token and return payload."""
