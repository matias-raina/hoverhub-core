from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException, status

from app.domain.models.session import UserSession
from app.domain.models.user import User
from app.domain.repositories.interfaces.session import ISessionRepository
from app.domain.repositories.interfaces.user import IUserRepository
from app.services.user import UserService


class TestUserServiceGetUserById:
    """Tests for UserService.get_user_by_id"""

    def test_get_user_by_id_success(self):
        """Test getting user by ID when user exists"""
        # Arrange
        user_id = uuid4()
        mock_user = User(
            id=user_id,
            email="test@example.com",
            hashed_password="hashed",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_user_repository.get_by_id.return_value = mock_user
        mock_session_repository = MagicMock(spec=ISessionRepository)

        service = UserService(mock_user_repository, mock_session_repository)

        # Act
        result = service.get_user_by_id(user_id)

        # Assert
        assert result == mock_user
        mock_user_repository.get_by_id.assert_called_once_with(user_id)

    def test_get_user_by_id_not_found(self):
        """Test getting user by ID when user doesn't exist"""
        # Arrange
        user_id = uuid4()
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_user_repository.get_by_id.return_value = None
        mock_session_repository = MagicMock(spec=ISessionRepository)

        service = UserService(mock_user_repository, mock_session_repository)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.get_user_by_id(user_id)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert f"User with ID {user_id} not found" in str(exc_info.value.detail)
        mock_user_repository.get_by_id.assert_called_once_with(user_id)


class TestUserServiceGetUserByEmail:
    """Tests for UserService.get_user_by_email"""

    def test_get_user_by_email_success(self):
        """Test getting user by email when user exists"""
        # Arrange
        email = "test@example.com"
        mock_user = User(
            id=uuid4(),
            email=email,
            hashed_password="hashed",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_user_repository.get_by_email.return_value = mock_user
        mock_session_repository = MagicMock(spec=ISessionRepository)

        service = UserService(mock_user_repository, mock_session_repository)

        # Act
        result = service.get_user_by_email(email)

        # Assert
        assert result == mock_user
        mock_user_repository.get_by_email.assert_called_once_with(email)

    def test_get_user_by_email_not_found(self):
        """Test getting user by email when user doesn't exist"""
        # Arrange
        email = "nonexistent@example.com"
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_user_repository.get_by_email.return_value = None
        mock_session_repository = MagicMock(spec=ISessionRepository)

        service = UserService(mock_user_repository, mock_session_repository)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.get_user_by_email(email)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert f"User with email {email} not found" in str(exc_info.value.detail)
        mock_user_repository.get_by_email.assert_called_once_with(email)


class TestUserServiceUpdateUser:
    """Tests for UserService.update_user"""

    def test_update_user_success_with_email(self):
        """Test updating user with email field"""
        # Arrange
        user_id = uuid4()
        original_email = "old@example.com"
        new_email = "new@example.com"
        original_updated_at = datetime(2023, 1, 1, tzinfo=timezone.utc)

        mock_user = User(
            id=user_id,
            email=original_email,
            hashed_password="hashed",
            is_active=True,
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            updated_at=original_updated_at,
        )

        updated_user = User(
            id=user_id,
            email=new_email,
            hashed_password="hashed",
            is_active=True,
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_user_repository.get_by_id.return_value = mock_user
        mock_user_repository.update.return_value = updated_user
        mock_session_repository = MagicMock(spec=ISessionRepository)

        service = UserService(mock_user_repository, mock_session_repository)

        # Act
        result = service.update_user(user_id, email=new_email)

        # Assert
        assert result == updated_user
        assert mock_user.email == new_email
        assert mock_user.updated_at != original_updated_at
        mock_user_repository.get_by_id.assert_called_once_with(user_id)
        mock_user_repository.update.assert_called_once()

    def test_update_user_success_without_email(self):
        """Test updating user without email field"""
        # Arrange
        user_id = uuid4()
        original_email = "test@example.com"
        original_updated_at = datetime(2023, 1, 1, tzinfo=timezone.utc)

        mock_user = User(
            id=user_id,
            email=original_email,
            hashed_password="hashed",
            is_active=True,
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            updated_at=original_updated_at,
        )

        updated_user = User(
            id=user_id,
            email=original_email,
            hashed_password="hashed",
            is_active=True,
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_user_repository.get_by_id.return_value = mock_user
        mock_user_repository.update.return_value = updated_user
        mock_session_repository = MagicMock(spec=ISessionRepository)

        service = UserService(mock_user_repository, mock_session_repository)

        # Act
        result = service.update_user(user_id)

        # Assert
        assert result == updated_user
        assert mock_user.email == original_email  # Email unchanged
        assert mock_user.updated_at != original_updated_at  # Updated timestamp changed
        mock_user_repository.get_by_id.assert_called_once_with(user_id)
        mock_user_repository.update.assert_called_once()

    def test_update_user_not_found(self):
        """Test updating user when user doesn't exist"""
        # Arrange
        user_id = uuid4()
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_user_repository.get_by_id.return_value = None
        mock_session_repository = MagicMock(spec=ISessionRepository)

        service = UserService(mock_user_repository, mock_session_repository)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.update_user(user_id, email="new@example.com")

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert f"User with ID {user_id} not found" in str(exc_info.value.detail)
        mock_user_repository.get_by_id.assert_called_once_with(user_id)
        mock_user_repository.update.assert_not_called()


class TestUserServiceDeleteUser:
    """Tests for UserService.delete_user"""

    def test_delete_user_success(self):
        """Test deleting user when user exists"""
        # Arrange
        user_id = uuid4()
        # Note: IUserRepository doesn't have delete in the interface, but UserService calls it
        # So we create a mock that allows the delete method
        mock_user_repository = MagicMock(spec=IUserRepository)
        # Add delete method to the mock (it's not in the interface but is called by the service)
        mock_user_repository.delete = MagicMock(return_value=True)
        mock_session_repository = MagicMock(spec=ISessionRepository)

        service = UserService(mock_user_repository, mock_session_repository)

        # Act
        result = service.delete_user(user_id)

        # Assert
        assert result is True
        mock_user_repository.delete.assert_called_once_with(user_id)

    def test_delete_user_not_found(self):
        """Test deleting user when user doesn't exist"""
        # Arrange
        user_id = uuid4()
        # Note: IUserRepository doesn't have delete in the interface, but UserService calls it
        # So we create a mock that allows the delete method
        mock_user_repository = MagicMock(spec=IUserRepository)
        # Add delete method to the mock (it's not in the interface but is called by the service)
        mock_user_repository.delete = MagicMock(return_value=False)
        mock_session_repository = MagicMock(spec=ISessionRepository)

        service = UserService(mock_user_repository, mock_session_repository)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.delete_user(user_id)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert f"User with ID {user_id} not found" in str(exc_info.value.detail)
        mock_user_repository.delete.assert_called_once_with(user_id)


class TestUserServiceGetUserSessions:
    """Tests for UserService.get_user_sessions"""

    def test_get_user_sessions_success(self):
        """Test getting user sessions when sessions exist"""
        # Arrange
        user_id = uuid4()
        session1 = UserSession(
            id=uuid4(),
            user_id=user_id,
            host="192.168.1.1",
            is_active=True,
            expires_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session2 = UserSession(
            id=uuid4(),
            user_id=user_id,
            host="192.168.1.2",
            is_active=True,
            expires_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        mock_sessions = [session1, session2]

        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_session_repository.get_all_by_user_id.return_value = mock_sessions

        service = UserService(mock_user_repository, mock_session_repository)

        # Act
        result = service.get_user_sessions(user_id)

        # Assert
        assert result == mock_sessions
        assert len(result) == 2
        mock_session_repository.get_all_by_user_id.assert_called_once_with(user_id)

    def test_get_user_sessions_empty(self):
        """Test getting user sessions when no sessions exist"""
        # Arrange
        user_id = uuid4()
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_session_repository.get_all_by_user_id.return_value = []

        service = UserService(mock_user_repository, mock_session_repository)

        # Act
        result = service.get_user_sessions(user_id)

        # Assert
        assert result == []
        assert len(result) == 0
        mock_session_repository.get_all_by_user_id.assert_called_once_with(user_id)

