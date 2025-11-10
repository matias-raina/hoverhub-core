from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.models.favorite import Favorite


class IFavoriteRepository(ABC):
    @abstractmethod
    def create(self, favorite: Favorite) -> Favorite:
        """Create a new favorite entry in the database."""

    @abstractmethod
    def get_by_id(self, favorite_id: UUID) -> Optional[Favorite]:
        """Retrieve a favorite entry by ID."""

    @abstractmethod
    def get_by_job_id(self, job_id: UUID) -> List[Favorite]:
        """Retrieve favorite entries by Job ID."""

    @abstractmethod
    def get_by_account_id(self, account_id: UUID) -> List[Favorite]:
        """Retrieve favorite entries by Account ID."""

    @abstractmethod
    def get_all(self, offset: int, limit: int) -> List[Favorite]:
        """Retrieve all favorite entries."""

    @abstractmethod
    def delete(self, favorite_id: UUID) -> bool:
        """Delete a favorite entry by ID."""
