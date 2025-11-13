from abc import ABC, abstractmethod
from typing import Optional, Sequence
from uuid import UUID

from app.domain.models.session import UserSession
from app.domain.models.user import User


class IUserService(ABC):
    @abstractmethod
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get a user by ID."""

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""

    @abstractmethod
    def update_user(self, user_id: UUID, **kwargs) -> User:
        """Update user information."""

    @abstractmethod
    def delete_user(self, user_id: UUID) -> bool:
        """Delete a user."""

    @abstractmethod
    def get_user_sessions(self, user_id: UUID) -> Sequence[UserSession]:
        """Get all sessions for a user."""
