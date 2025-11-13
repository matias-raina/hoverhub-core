from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models.user import User


class IUserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User:
        """Create a new user in the database."""

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        """Retrieve a user by email."""

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None:
        """Retrieve a user by ID."""

    @abstractmethod
    def update(self, user: User) -> User:
        """Update an existing user."""
