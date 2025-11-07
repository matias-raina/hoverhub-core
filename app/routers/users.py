from fastapi import APIRouter, HTTPException, status

from app.config.dependencies import CurrentUserDep, UserServiceDep

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user(current_user: CurrentUserDep):
    """
    Get the currently authenticated user.

    Args:
        current_user: The authenticated user from JWT token

    Returns:
        Current user information
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat(),
    }


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(
    user_id: str,
    _current_user: CurrentUserDep,
    user_service: UserServiceDep,
):
    """
    Get a user by ID (requires authentication).

    Args:
        user_id: The ID of the user to retrieve
        _current_user: The authenticated user (ensures auth is required)
        user_service: Injected user service

    Returns:
        User information
    """
    user = user_service.get_user_by_id(user_id)
    return {
        "id": str(user.id),
        "email": user.email,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
    }


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: CurrentUserDep,
    user_service: UserServiceDep,
):
    """
    Delete a user by ID (requires authentication, user can only delete themselves).

    Args:
        user_id: The ID of the user to delete
        current_user: The authenticated user
        user_service: Injected user service

    Returns:
        No content
    """
    # Users can only delete their own account
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account",
        )

    user_service.delete_user(user_id)
    return None
