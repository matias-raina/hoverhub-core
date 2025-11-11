from abc import ABC, abstractmethod
from typing import Sequence, Optional
from uuid import UUID

from app.domain.models.favorite import Favorite
from app.dto.favorite import CreateFavoriteDto


class IFavoriteService(ABC):
    @abstractmethod
    def create_favorite(self, account_id: UUID, dto: CreateFavoriteDto) -> Favorite:
        """Create a new favorite entry."""

    @abstractmethod
    def get_favorite_by_id(self, favorite_id: UUID) -> Optional[Favorite]:
        """Retrieve a favorite entry by ID."""

    @abstractmethod
    def get_favorites_by_account_id(self, account_id: UUID) -> Sequence[Favorite]:
        """Retrieve favorite entries by Account ID."""

    @abstractmethod
    def delete_favorite(self, account_id: UUID, favorite_id: UUID) -> bool:
        """Delete a favorite entry by ID."""
