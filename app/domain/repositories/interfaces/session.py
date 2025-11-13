from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from app.domain.models.session import UserSession


class ISessionRepository(ABC):
    @abstractmethod
    def create(self, session: UserSession) -> UserSession:
        """Create a new session in the database."""

    @abstractmethod
    def get_by_id(self, session_id: UUID) -> UserSession | None:
        """Get a session by its ID."""

    @abstractmethod
    def deactivate(self, session_id: UUID) -> UserSession | None:
        """Deactivate an existing session and return the updated session."""

    @abstractmethod
    def update(self, session: UserSession) -> UserSession | None:
        """Update an existing session and return the updated session."""

    @abstractmethod
    def get_all_by_user_id(self, user_id: UUID) -> Sequence[UserSession]:
        """Retrieve all sessions by user ID."""

    @abstractmethod
    def deactivate_expired_sessions(self) -> int:
        """Deactivate all expired sessions and return the count of deactivated sessions."""
