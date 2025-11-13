"""Tests for FastAPI dependency functions."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.config.dependencies import get_authenticated_account
from app.domain.models.account import Account, AccountType
from app.services.interfaces import IAuthService


class TestGetAuthenticatedAccount:
    """Tests for get_authenticated_account dependency function."""

    def test_get_authenticated_account_success(self):
        """Test getting authenticated account successfully with valid UUID."""
        # Arrange
        account_id = uuid4()
        token = "test-token"
        mock_account = Account(
            id=account_id,
            user_id=uuid4(),
            name="Test Account",
            account_type=AccountType.EMPLOYER,
            is_active=True,
        )

        mock_auth_service = MagicMock(spec=IAuthService)
        mock_auth_service.get_authenticated_account.return_value = mock_account

        mock_credentials = MagicMock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = token

        # Act
        result = get_authenticated_account(
            credentials=mock_credentials,
            auth_service=mock_auth_service,
            x_account_id=str(account_id),
        )

        # Assert
        assert result == mock_account
        mock_auth_service.get_authenticated_account.assert_called_once_with(token, account_id)

    def test_get_authenticated_account_invalid_uuid_format(self):
        """Test that invalid UUID format raises HTTPException."""
        # Arrange
        mock_auth_service = MagicMock(spec=IAuthService)
        mock_credentials = MagicMock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = "test-token"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_authenticated_account(
                credentials=mock_credentials,
                auth_service=mock_auth_service,
                x_account_id="invalid-uuid-format",
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid account ID format" in exc_info.value.detail
        # Should not call auth service if UUID is invalid
        mock_auth_service.get_authenticated_account.assert_not_called()

    def test_get_authenticated_account_empty_string(self):
        """Test that empty string UUID raises HTTPException."""
        # Arrange
        mock_auth_service = MagicMock(spec=IAuthService)
        mock_credentials = MagicMock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = "test-token"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_authenticated_account(
                credentials=mock_credentials,
                auth_service=mock_auth_service,
                x_account_id="",
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid account ID format" in exc_info.value.detail
        mock_auth_service.get_authenticated_account.assert_not_called()

    def test_get_authenticated_account_propagates_auth_service_errors(self):
        """Test that errors from auth service are propagated."""
        # Arrange
        account_id = uuid4()
        token = "test-token"
        mock_auth_service = MagicMock(spec=IAuthService)
        mock_auth_service.get_authenticated_account.side_effect = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

        mock_credentials = MagicMock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = token

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_authenticated_account(
                credentials=mock_credentials,
                auth_service=mock_auth_service,
                x_account_id=str(account_id),
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Not authorized" in exc_info.value.detail
        mock_auth_service.get_authenticated_account.assert_called_once_with(token, account_id)
