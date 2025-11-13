from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException, status

from app.domain.models.favorite import Favorite
from app.domain.repositories.interfaces.favorite import IFavoriteRepository
from app.services.favorite import FavoriteService


class TestFavoriteServiceDeleteFavorite:
    """Tests for FavoriteService.delete_favorite"""

    def test_delete_favorite_success(self):
        """Test deleting a favorite successfully"""
        # Arrange
        account_id = uuid4()
        favorite_id = uuid4()
        job_id = uuid4()

        mock_favorite = Favorite(
            id=favorite_id,
            account_id=account_id,
            job_id=job_id,
            created_at=datetime.now(timezone.utc),
        )

        mock_favorite_repository = MagicMock(spec=IFavoriteRepository)
        mock_favorite_repository.get_by_id.return_value = mock_favorite
        mock_favorite_repository.delete.return_value = True

        service = FavoriteService(mock_favorite_repository)

        # Act
        result = service.delete_favorite(account_id, favorite_id)

        # Assert
        assert result is True
        mock_favorite_repository.get_by_id.assert_called_once_with(favorite_id)
        mock_favorite_repository.delete.assert_called_once_with(favorite_id)

    def test_delete_favorite_not_found_from_get_by_id(self):
        """Test deleting a favorite when get_favorite_by_id returns None"""
        # Arrange
        account_id = uuid4()
        favorite_id = uuid4()

        mock_favorite_repository = MagicMock(spec=IFavoriteRepository)
        mock_favorite_repository.get_by_id.return_value = None

        service = FavoriteService(mock_favorite_repository)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.delete_favorite(account_id, favorite_id)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Favorite not found" in str(exc_info.value.detail)
        mock_favorite_repository.get_by_id.assert_called_once_with(favorite_id)
        mock_favorite_repository.delete.assert_not_called()

    def test_delete_favorite_not_found_from_delete(self):
        """Test deleting a favorite when repository.delete returns False"""
        # Arrange
        account_id = uuid4()
        favorite_id = uuid4()
        job_id = uuid4()

        mock_favorite = Favorite(
            id=favorite_id,
            account_id=account_id,
            job_id=job_id,
            created_at=datetime.now(timezone.utc),
        )

        mock_favorite_repository = MagicMock(spec=IFavoriteRepository)
        mock_favorite_repository.get_by_id.return_value = mock_favorite
        mock_favorite_repository.delete.return_value = False

        service = FavoriteService(mock_favorite_repository)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.delete_favorite(account_id, favorite_id)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Favorite not found" in str(exc_info.value.detail)
        mock_favorite_repository.get_by_id.assert_called_once_with(favorite_id)
        mock_favorite_repository.delete.assert_called_once_with(favorite_id)

    def test_delete_favorite_unauthorized(self):
        """Test deleting a favorite when account_id doesn't match"""
        # Arrange
        account_id = uuid4()
        other_account_id = uuid4()
        favorite_id = uuid4()
        job_id = uuid4()

        mock_favorite = Favorite(
            id=favorite_id,
            account_id=other_account_id,  # Different account
            job_id=job_id,
            created_at=datetime.now(timezone.utc),
        )

        mock_favorite_repository = MagicMock(spec=IFavoriteRepository)
        mock_favorite_repository.get_by_id.return_value = mock_favorite

        service = FavoriteService(mock_favorite_repository)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.delete_favorite(account_id, favorite_id)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Not authorized" in str(exc_info.value.detail)
        mock_favorite_repository.get_by_id.assert_called_once_with(favorite_id)
        mock_favorite_repository.delete.assert_not_called()
