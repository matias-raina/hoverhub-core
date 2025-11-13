from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, status

from app.domain.models.favorite import Favorite
from app.domain.repositories.interfaces.favorite import IFavoriteRepository
from app.dto.favorite import CreateFavoriteDto
from app.services.interfaces.favorite import IFavoriteService


class FavoriteService(IFavoriteService):
    def __init__(self, favorite_repository: IFavoriteRepository):
        self.favorite_repository = favorite_repository

    def create_favorite(self, account_id: UUID, dto: CreateFavoriteDto) -> Favorite:
        """Create a new favorite entry."""
        favorite = Favorite(account_id=account_id, job_id=dto.job_id)
        return self.favorite_repository.create(favorite)

    def get_favorite_by_id(self, favorite_id: UUID) -> Favorite | None:
        """Retrieve a favorite entry by ID."""
        favorite = self.favorite_repository.get_by_id(favorite_id)
        if not favorite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Favorite not found",
            )
        return favorite

    def get_favorites_by_account_id(self, account_id: UUID) -> Sequence[Favorite]:
        """Retrieve favorite entries by Account ID."""
        return self.favorite_repository.get_by_account_id(account_id)

    def delete_favorite(self, account_id: UUID, favorite_id: UUID) -> bool:
        """Delete a favorite entry by ID."""
        favorite = self.get_favorite_by_id(favorite_id)
        if favorite.account_id != account_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this favorite",
            )
        success = self.favorite_repository.delete(favorite_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Favorite not found",
            )
        return success
