from uuid import UUID

from fastapi import APIRouter, status

from app.config.dependencies import AccountContextDep, FavoriteServiceDep
from app.dto.favorite import CreateFavoriteDto

router = APIRouter(prefix="/jobs/favorites", tags=["Favorites"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_favorite(
    account_context: AccountContextDep,
    dto: CreateFavoriteDto,
    favorite_service: FavoriteServiceDep,
):
    """
    Create a new favorite entry.

    Args:
        account_context: The account context from authentication
        dto: The favorite data to create
        favorite_service: Injected favorite service

    Returns:
        The created favorite information
    """
    favorite = favorite_service.create_favorite(account_context.id, dto)
    return {
        "id": favorite.id,
        "account_id": favorite.account_id,
        "job_id": favorite.job_id,
        "created_at": favorite.created_at,
    }


@router.get("/", status_code=status.HTTP_200_OK)
async def get_favorites(
    account_context: AccountContextDep,
    favorite_service: FavoriteServiceDep,
):
    """
    Get all favorite entries for a specific account.

    Args:
        account_context: The account context from authentication
        favorite_service: Injected favorite service

    Returns:
        List of favorite information
    """
    favorites = favorite_service.get_favorites_by_account_id(account_context.id)
    return [
        {
            "id": favorite.id,
            "account_id": favorite.account_id,
            "job_id": favorite.job_id,
            "created_at": favorite.created_at,
        }
        for favorite in favorites
    ]


@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite(
    account_context: AccountContextDep,
    favorite_id: UUID,
    favorite_service: FavoriteServiceDep,
):
    """
    Delete a favorite entry by ID.

    Args:
        account_context: The account context from authentication
        favorite_id: The ID of the favorite to delete
        favorite_service: Injected favorite service

    Returns:
        Deletion success status
    """
    favorite_service.delete_favorite(account_context.id, favorite_id)
