from abc import ABC, abstractmethod
from typing import Optional

from app.domain.models.user import User


class IUserService(ABC):
    @abstractmethod
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""

    @abstractmethod
    def update_user(self, user_id: str, **kwargs) -> User:
        """Update user information."""

    @abstractmethod
    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
