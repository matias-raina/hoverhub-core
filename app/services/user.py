from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status

from app.domain.models.user import User
from app.domain.repositories.interfaces.user import IUserRepository
from app.services.interfaces.user import IUserService


class UserService(IUserService):
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        user = self.user_repository.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email {email} not found",
            )
        return user

    def update_user(self, user_id: str, **kwargs) -> User:
        """Update user information."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )

        # Update allowed fields
        if "email" in kwargs:
            user.email = kwargs["email"]

        user.updated_at = datetime.now(timezone.utc)
        return self.user_repository.update(user)

    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        success = self.user_repository.delete(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )
        return success
