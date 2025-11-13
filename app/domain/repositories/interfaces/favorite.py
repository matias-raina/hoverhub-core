from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from app.domain.models.favorite import Favorite


class IFavoriteRepository(ABC):
    @abstractmethod
    def create(self, favorite: Favorite) -> Favorite:
        """Create a new favorite entry in the database."""

    @abstractmethod
    def get_by_id(self, favorite_id: UUID) -> Favorite | None:
        """Retrieve a favorite entry by ID."""

    @abstractmethod
    def get_by_account_id(self, account_id: UUID) -> Sequence[Favorite]:
        """Retrieve favorite entries by Account ID."""

    @abstractmethod
    def get_all(self, offset: int, limit: int) -> Sequence[Favorite]:
        """Retrieve all favorite entries."""

    @abstractmethod
    def delete(self, favorite_id: UUID) -> bool:
        """Delete a favorite entry by ID."""
