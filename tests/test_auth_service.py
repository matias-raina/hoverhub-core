import datetime
from datetime import datetime as dt
from unittest.mock import MagicMock
from uuid import uuid4

import jwt
import pytest
from fastapi import HTTPException, status

from app.domain.models.account import Account, AccountType
from app.domain.models.session import UserSession
from app.domain.models.user import User
from app.domain.repositories.interfaces.account import IAccountRepository
from app.domain.repositories.interfaces.auth import IAuthRepository, JwtTokenPayload, JwtTokenType
from app.domain.repositories.interfaces.session import ISessionRepository
from app.domain.repositories.interfaces.user import IUserRepository
from app.services.auth import AuthService


class TestAuthServiceDecodeTokenSafely:
    """Tests for AuthService._decode_token_safely"""

    def test_decode_token_safely_success(self):
        """Test successful token decoding"""
        # Arrange
        user_id = uuid4()
        session_id = uuid4()
        jti = "test-jti"
        exp = int(dt.now(datetime.UTC).timestamp()) + 3600

        mock_payload = {
            "sub": str(user_id),
            "sid": str(session_id),
            "type": JwtTokenType.ACCESS.value,
            "iat": int(dt.now(datetime.UTC).timestamp()),
            "exp": exp,
            "jti": jti,
        }

        mock_cache = MagicMock()
        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_auth_repository.decode_token.return_value = mock_payload
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act
        result = service._decode_token_safely("test-token", JwtTokenType.ACCESS)

        # Assert
        assert isinstance(result, JwtTokenPayload)
        assert result.sub == user_id
        assert result.sid == session_id
        assert result.type == JwtTokenType.ACCESS

    def test_decode_token_safely_expired_signature(self):
        """Test token decoding with expired signature"""
        # Arrange
        mock_cache = MagicMock()
        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_auth_repository.decode_token.side_effect = jwt.ExpiredSignatureError("Token expired")
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service._decode_token_safely("expired-token", JwtTokenType.ACCESS)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "expired" in str(exc_info.value.detail).lower()

    def test_decode_token_safely_invalid_token(self):
        """Test token decoding with invalid token"""
        # Arrange
        mock_cache = MagicMock()
        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_auth_repository.decode_token.side_effect = jwt.InvalidTokenError("Invalid token")
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service._decode_token_safely("invalid-token", JwtTokenType.ACCESS)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in str(exc_info.value.detail).lower()

    def test_decode_token_safely_invalid_payload(self):
        """Test token decoding with invalid payload structure"""
        # Arrange
        mock_cache = MagicMock()
        mock_auth_repository = MagicMock(spec=IAuthRepository)
        # Return payload missing required fields
        mock_auth_repository.decode_token.return_value = {"invalid": "payload"}
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service._decode_token_safely("token", JwtTokenType.ACCESS)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in str(exc_info.value.detail).lower()

    def test_decode_token_safely_wrong_token_type(self):
        """Test token decoding with wrong token type"""
        # Arrange
        user_id = uuid4()
        session_id = uuid4()
        jti = "test-jti"
        exp = int(dt.now(datetime.UTC).timestamp()) + 3600

        mock_payload = {
            "sub": str(user_id),
            "sid": str(session_id),
            "type": JwtTokenType.REFRESH.value,  # Wrong type
            "iat": int(dt.now(datetime.UTC).timestamp()),
            "exp": exp,
            "jti": jti,
        }

        mock_cache = MagicMock()
        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_auth_repository.decode_token.return_value = mock_payload
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service._decode_token_safely("token", JwtTokenType.ACCESS)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "token type" in str(exc_info.value.detail).lower()


class TestAuthServiceCheckTokenBlacklist:
    """Tests for AuthService._check_token_blacklist"""

    def test_check_token_blacklist_not_blacklisted(self):
        """Test checking token that is not blacklisted"""
        # Arrange
        jti = "test-jti"
        mock_cache = MagicMock()
        mock_cache.get.return_value = None  # Not blacklisted
        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act - should not raise exception
        service._check_token_blacklist(jti)

        # Assert
        mock_cache.get.assert_called_once_with(f"blacklist:{jti}")

    def test_check_token_blacklisted(self):
        """Test checking token that is blacklisted"""
        # Arrange
        jti = "blacklisted-jti"
        mock_cache = MagicMock()
        mock_cache.get.return_value = "1"  # Blacklisted
        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service._check_token_blacklist(jti)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "revoked" in str(exc_info.value.detail).lower()
        mock_cache.get.assert_called_once_with(f"blacklist:{jti}")

    def test_check_token_blacklist_none_jti(self):
        """Test checking token with None jti"""
        # Arrange
        mock_cache = MagicMock()
        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act - should not raise exception when jti is None
        service._check_token_blacklist(None)

        # Assert - should not call cache.get when jti is None
        mock_cache.get.assert_not_called()


class TestAuthServiceValidateTokenPayload:
    """Tests for AuthService._validate_token_payload"""

    def test_validate_token_payload_success(self):
        """Test validating token payload with all required keys"""
        # Arrange
        user_id = uuid4()
        session_id = uuid4()
        jti = "test-jti"
        exp = int(dt.now(datetime.UTC).timestamp()) + 3600

        payload = JwtTokenPayload(
            sub=user_id,
            sid=session_id,
            type=JwtTokenType.ACCESS,
            iat=int(dt.now(datetime.UTC).timestamp()),
            exp=exp,
            jti=jti,
        )

        mock_cache = MagicMock()
        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act - should not raise exception
        service._validate_token_payload(payload, ["sub", "sid"])

    def test_validate_token_payload_missing_key(self):
        """Test validating token payload with missing required key"""
        # Arrange
        user_id = uuid4()
        session_id = uuid4()
        jti = "test-jti"
        exp = int(dt.now(datetime.UTC).timestamp()) + 3600

        # Create a mock payload that doesn't have the required attribute
        class MockPayload:
            def __init__(self):
                self.sub = user_id
                # Missing sid

        mock_payload = MockPayload()

        mock_cache = MagicMock()
        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service._validate_token_payload(mock_payload, ["sub", "sid"])

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "sid" in str(exc_info.value.detail).lower()


class TestAuthServiceValidateSession:
    """Tests for AuthService._validate_session"""

    def test_validate_session_success(self):
        """Test validating active, non-expired session"""
        # Arrange
        session_id = uuid4()
        user_id = uuid4()
        expires_at = dt.now(datetime.UTC) + datetime.timedelta(hours=1)

        mock_session = UserSession(
            id=session_id,
            user_id=user_id,
            host="127.0.0.1",
            is_active=True,
            expires_at=expires_at,
            created_at=dt.now(datetime.UTC),
            updated_at=dt.now(datetime.UTC),
        )

        mock_cache = MagicMock()
        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_session_repository.get_by_id.return_value = mock_session
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act
        result = service._validate_session(session_id)

        # Assert
        assert result == mock_session
        mock_session_repository.get_by_id.assert_called_once_with(session_id)

    def test_validate_session_not_found(self):
        """Test validating session that doesn't exist"""
        # Arrange
        session_id = uuid4()

        mock_cache = MagicMock()
        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_session_repository.get_by_id.return_value = None
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service._validate_session(session_id)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "revoked" in str(exc_info.value.detail).lower()

    def test_validate_session_inactive(self):
        """Test validating inactive session"""
        # Arrange
        session_id = uuid4()
        user_id = uuid4()
        expires_at = dt.now(datetime.UTC) + datetime.timedelta(hours=1)

        mock_session = UserSession(
            id=session_id,
            user_id=user_id,
            host="127.0.0.1",
            is_active=False,  # Inactive
            expires_at=expires_at,
            created_at=dt.now(datetime.UTC),
            updated_at=dt.now(datetime.UTC),
        )

        mock_cache = MagicMock()
        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_session_repository.get_by_id.return_value = mock_session
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service._validate_session(session_id)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "revoked" in str(exc_info.value.detail).lower()

    def test_validate_session_expired(self):
        """Test validating expired session"""
        # Arrange
        session_id = uuid4()
        user_id = uuid4()
        expires_at = dt.now(datetime.UTC) - datetime.timedelta(hours=1)  # Expired

        mock_session = UserSession(
            id=session_id,
            user_id=user_id,
            host="127.0.0.1",
            is_active=True,
            expires_at=expires_at,
            created_at=dt.now(datetime.UTC),
            updated_at=dt.now(datetime.UTC),
        )

        mock_cache = MagicMock()
        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_session_repository.get_by_id.return_value = mock_session
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service._validate_session(session_id)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "expired" in str(exc_info.value.detail).lower()
        # Should deactivate the expired session
        mock_session_repository.deactivate.assert_called_once_with(session_id)


class TestAuthServiceValidateUserExistsAndActive:
    """Tests for AuthService._validate_user_exists_and_active"""

    def test_validate_user_exists_and_active_success(self):
        """Test validating active user"""
        # Arrange
        user_id = uuid4()

        mock_user = User(
            id=user_id,
            email="test@example.com",
            hashed_password="hashed",
            is_active=True,
            created_at=dt.now(datetime.UTC),
            updated_at=dt.now(datetime.UTC),
        )

        mock_cache = MagicMock()
        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_user_repository.get_by_id.return_value = mock_user
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act
        result = service._validate_user_exists_and_active(user_id)

        # Assert
        assert result == mock_user
        mock_user_repository.get_by_id.assert_called_once_with(user_id)

    def test_validate_user_exists_and_active_not_found(self):
        """Test validating user that doesn't exist"""
        # Arrange
        user_id = uuid4()

        mock_cache = MagicMock()
        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_user_repository.get_by_id.return_value = None
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service._validate_user_exists_and_active(user_id)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "not found" in str(exc_info.value.detail).lower()

    def test_validate_user_exists_and_active_inactive(self):
        """Test validating inactive user"""
        # Arrange
        user_id = uuid4()

        mock_user = User(
            id=user_id,
            email="test@example.com",
            hashed_password="hashed",
            is_active=False,  # Inactive
            created_at=dt.now(datetime.UTC),
            updated_at=dt.now(datetime.UTC),
        )

        mock_cache = MagicMock()
        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_user_repository.get_by_id.return_value = mock_user
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service._validate_user_exists_and_active(user_id)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "inactive" in str(exc_info.value.detail).lower()


class TestAuthServiceGetAuthenticatedAccount:
    """Tests for AuthService.get_authenticated_account"""

    def test_get_authenticated_account_success(self):
        """Test getting authenticated account successfully"""
        # Arrange
        user_id = uuid4()
        account_id = uuid4()
        session_id = uuid4()
        jti = "test-jti"
        exp = int(dt.now(datetime.UTC).timestamp()) + 3600

        mock_user = User(
            id=user_id,
            email="test@example.com",
            hashed_password="hashed",
            is_active=True,
            created_at=dt.now(datetime.UTC),
            updated_at=dt.now(datetime.UTC),
        )

        mock_account = Account(
            id=account_id,
            user_id=user_id,
            name="Test Account",
            account_type=AccountType.EMPLOYER,
            is_active=True,
            created_at=dt.now(datetime.UTC),
            updated_at=dt.now(datetime.UTC),
        )

        mock_payload = JwtTokenPayload(
            sub=user_id,
            sid=session_id,
            type=JwtTokenType.ACCESS,
            iat=int(dt.now(datetime.UTC).timestamp()),
            exp=exp,
            jti=jti,
        )

        expires_at = dt.now(datetime.UTC) + datetime.timedelta(hours=1)
        mock_session = UserSession(
            id=session_id,
            user_id=user_id,
            host="127.0.0.1",
            is_active=True,
            expires_at=expires_at,
            created_at=dt.now(datetime.UTC),
            updated_at=dt.now(datetime.UTC),
        )

        mock_cache = MagicMock()
        mock_cache.get.return_value = None  # Not blacklisted

        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_auth_repository.decode_token.return_value = {
            "sub": str(user_id),
            "sid": str(session_id),
            "type": JwtTokenType.ACCESS.value,
            "iat": int(dt.now(datetime.UTC).timestamp()),
            "exp": exp,
            "jti": jti,
        }

        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_user_repository.get_by_id.return_value = mock_user

        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_session_repository.get_by_id.return_value = mock_session

        mock_account_repository = MagicMock(spec=IAccountRepository)
        mock_account_repository.get_by_id.return_value = mock_account

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act
        result = service.get_authenticated_account("test-token", account_id)

        # Assert
        assert result == mock_account
        mock_account_repository.get_by_id.assert_called_once_with(account_id)

    def test_get_authenticated_account_not_found(self):
        """Test getting account that doesn't exist"""
        # Arrange
        user_id = uuid4()
        account_id = uuid4()
        session_id = uuid4()
        jti = "test-jti"
        exp = int(dt.now(datetime.UTC).timestamp()) + 3600

        mock_user = User(
            id=user_id,
            email="test@example.com",
            hashed_password="hashed",
            is_active=True,
            created_at=dt.now(datetime.UTC),
            updated_at=dt.now(datetime.UTC),
        )

        mock_payload = JwtTokenPayload(
            sub=user_id,
            sid=session_id,
            type=JwtTokenType.ACCESS,
            iat=int(dt.now(datetime.UTC).timestamp()),
            exp=exp,
            jti=jti,
        )

        expires_at = dt.now(datetime.UTC) + datetime.timedelta(hours=1)
        mock_session = UserSession(
            id=session_id,
            user_id=user_id,
            host="127.0.0.1",
            is_active=True,
            expires_at=expires_at,
            created_at=dt.now(datetime.UTC),
            updated_at=dt.now(datetime.UTC),
        )

        mock_cache = MagicMock()
        mock_cache.get.return_value = None

        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_auth_repository.decode_token.return_value = {
            "sub": str(user_id),
            "sid": str(session_id),
            "type": JwtTokenType.ACCESS.value,
            "iat": int(dt.now(datetime.UTC).timestamp()),
            "exp": exp,
            "jti": jti,
        }

        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_user_repository.get_by_id.return_value = mock_user

        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_session_repository.get_by_id.return_value = mock_session

        mock_account_repository = MagicMock(spec=IAccountRepository)
        mock_account_repository.get_by_id.return_value = None  # Account not found

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.get_authenticated_account("test-token", account_id)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Account not found" in str(exc_info.value.detail)

    def test_get_authenticated_account_unauthorized(self):
        """Test getting account that belongs to different user"""
        # Arrange
        user_id = uuid4()
        other_user_id = uuid4()
        account_id = uuid4()
        session_id = uuid4()
        jti = "test-jti"
        exp = int(dt.now(datetime.UTC).timestamp()) + 3600

        mock_user = User(
            id=user_id,
            email="test@example.com",
            hashed_password="hashed",
            is_active=True,
            created_at=dt.now(datetime.UTC),
            updated_at=dt.now(datetime.UTC),
        )

        mock_account = Account(
            id=account_id,
            user_id=other_user_id,  # Different user
            name="Test Account",
            account_type=AccountType.EMPLOYER,
            is_active=True,
            created_at=dt.now(datetime.UTC),
            updated_at=dt.now(datetime.UTC),
        )

        expires_at = dt.now(datetime.UTC) + datetime.timedelta(hours=1)
        mock_session = UserSession(
            id=session_id,
            user_id=user_id,
            host="127.0.0.1",
            is_active=True,
            expires_at=expires_at,
            created_at=dt.now(datetime.UTC),
            updated_at=dt.now(datetime.UTC),
        )

        mock_cache = MagicMock()
        mock_cache.get.return_value = None

        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_auth_repository.decode_token.return_value = {
            "sub": str(user_id),
            "sid": str(session_id),
            "type": JwtTokenType.ACCESS.value,
            "iat": int(dt.now(datetime.UTC).timestamp()),
            "exp": exp,
            "jti": jti,
        }

        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_user_repository.get_by_id.return_value = mock_user

        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_session_repository.get_by_id.return_value = mock_session

        mock_account_repository = MagicMock(spec=IAccountRepository)
        mock_account_repository.get_by_id.return_value = mock_account

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.get_authenticated_account("test-token", account_id)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "not authorized" in str(exc_info.value.detail).lower()


class TestAuthServiceGetAuthenticatedUser:
    """Tests for AuthService.get_authenticated_user"""

    def test_get_authenticated_user_success(self):
        """Test getting authenticated user successfully"""
        # Arrange
        user_id = uuid4()
        session_id = uuid4()
        jti = "test-jti"
        exp = int(dt.now(datetime.UTC).timestamp()) + 3600

        mock_user = User(
            id=user_id,
            email="test@example.com",
            hashed_password="hashed",
            is_active=True,
            created_at=dt.now(datetime.UTC),
            updated_at=dt.now(datetime.UTC),
        )

        expires_at = dt.now(datetime.UTC) + datetime.timedelta(hours=1)
        mock_session = UserSession(
            id=session_id,
            user_id=user_id,
            host="127.0.0.1",
            is_active=True,
            expires_at=expires_at,
            created_at=dt.now(datetime.UTC),
            updated_at=dt.now(datetime.UTC),
        )

        mock_cache = MagicMock()
        mock_cache.get.return_value = None  # Not blacklisted

        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_auth_repository.decode_token.return_value = {
            "sub": str(user_id),
            "sid": str(session_id),
            "type": JwtTokenType.ACCESS.value,
            "iat": int(dt.now(datetime.UTC).timestamp()),
            "exp": exp,
            "jti": jti,
        }

        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_user_repository.get_by_id.return_value = mock_user

        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_session_repository.get_by_id.return_value = mock_session

        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act
        result = service.get_authenticated_user("test-token")

        # Assert
        assert result == mock_user
        mock_auth_repository.decode_token.assert_called_once_with("test-token")
        mock_cache.get.assert_called_once_with(f"blacklist:{jti}")
        mock_user_repository.get_by_id.assert_called_once_with(user_id)


class TestAuthServiceRefreshToken:
    """Tests for AuthService.refresh_token"""

    def test_refresh_token_success(self):
        """Test refreshing token successfully"""
        # Arrange
        user_id = uuid4()
        session_id = uuid4()
        jti = "old-jti"
        exp = int(dt.now(datetime.UTC).timestamp()) + 3600

        expires_at = dt.now(datetime.UTC) + datetime.timedelta(hours=1)
        new_expires_at = dt.now(datetime.UTC) + datetime.timedelta(hours=2)
        mock_session = UserSession(
            id=session_id,
            user_id=user_id,
            host="127.0.0.1",
            is_active=True,
            expires_at=expires_at,
            created_at=dt.now(datetime.UTC),
            updated_at=dt.now(datetime.UTC),
        )

        mock_cache = MagicMock()
        mock_cache.get.return_value = None  # Not blacklisted
        mock_cache.setex.return_value = True

        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_auth_repository.decode_token.return_value = {
            "sub": str(user_id),
            "sid": str(session_id),
            "type": JwtTokenType.REFRESH.value,
            "iat": int(dt.now(datetime.UTC).timestamp()),
            "exp": exp,
            "jti": jti,
        }
        mock_auth_repository.create_token.return_value = (
            "new-access-token",
            "new-refresh-token",
            new_expires_at,
        )

        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_session_repository.get_by_id.return_value = mock_session
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act
        access_token, refresh_token = service.refresh_token("old-refresh-token")

        # Assert
        assert access_token == "new-access-token"
        assert refresh_token == "new-refresh-token"
        mock_auth_repository.decode_token.assert_called_once_with("old-refresh-token")
        mock_auth_repository.create_token.assert_called_once()
        mock_session_repository.update.assert_called_once()
        # Should blacklist the old token
        mock_cache.setex.assert_called_once()


class TestAuthServiceSignout:
    """Tests for AuthService.signout"""

    def test_signout_success(self):
        """Test signing out successfully"""
        # Arrange
        user_id = uuid4()
        session_id = uuid4()
        jti = "test-jti"
        exp = int(dt.now(datetime.UTC).timestamp()) + 3600

        mock_cache = MagicMock()
        mock_cache.setex.return_value = True

        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_auth_repository.decode_token.return_value = {
            "sub": str(user_id),
            "sid": str(session_id),
            "type": JwtTokenType.ACCESS.value,
            "iat": int(dt.now(datetime.UTC).timestamp()),
            "exp": exp,
            "jti": jti,
        }

        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act
        result = service.signout("test-token")

        # Assert
        assert result is True
        mock_auth_repository.decode_token.assert_called_once_with("test-token")
        mock_session_repository.deactivate.assert_called_once_with(session_id)
        mock_cache.setex.assert_called_once()


class TestAuthServiceBlacklistToken:
    """Tests for AuthService._blacklist_token"""

    def test_blacklist_token_success(self):
        """Test blacklisting token successfully"""
        # Arrange
        jti = "test-jti"
        exp = int(dt.now(datetime.UTC).timestamp()) + 3600  # Future expiration

        mock_cache = MagicMock()
        mock_cache.setex.return_value = True

        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act
        service._blacklist_token(jti, exp)

        # Assert
        mock_cache.setex.assert_called_once()
        call_args = mock_cache.setex.call_args[0]
        assert call_args[0] == f"blacklist:{jti}"
        assert call_args[1] > 0  # TTL should be positive
        assert call_args[2] == "1"

    def test_blacklist_token_expired(self):
        """Test blacklisting token that's already expired"""
        # Arrange
        jti = "test-jti"
        exp = int(dt.now(datetime.UTC).timestamp()) - 3600  # Past expiration

        mock_cache = MagicMock()
        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act
        service._blacklist_token(jti, exp)

        # Assert - should not call setex when TTL is negative
        mock_cache.setex.assert_not_called()

    def test_blacklist_token_none_jti(self):
        """Test blacklisting token with None jti"""
        # Arrange
        exp = int(dt.now(datetime.UTC).timestamp()) + 3600

        mock_cache = MagicMock()
        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act
        service._blacklist_token(None, exp)

        # Assert - should not call setex when jti is None
        mock_cache.setex.assert_not_called()

    def test_blacklist_token_none_exp(self):
        """Test blacklisting token with None exp"""
        # Arrange
        jti = "test-jti"

        mock_cache = MagicMock()
        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act
        service._blacklist_token(jti, None)

        # Assert - should not call setex when exp is None
        mock_cache.setex.assert_not_called()


class TestAuthServiceCalculateTokenTTL:
    """Tests for AuthService._calculate_token_ttl"""

    def test_calculate_token_ttl_success(self):
        """Test calculating token TTL"""
        # Arrange
        exp = int(dt.now(datetime.UTC).timestamp()) + 3600  # 1 hour from now

        mock_cache = MagicMock()
        mock_auth_repository = MagicMock(spec=IAuthRepository)
        mock_user_repository = MagicMock(spec=IUserRepository)
        mock_session_repository = MagicMock(spec=ISessionRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)

        service = AuthService(
            mock_cache,
            mock_auth_repository,
            mock_user_repository,
            mock_session_repository,
            mock_account_repository,
        )

        # Act
        ttl = service._calculate_token_ttl(exp)

        # Assert
        assert isinstance(ttl, int)
        assert ttl > 0
        assert ttl <= 3600  # Should be close to 3600 (within a few seconds)
