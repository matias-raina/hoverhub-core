import datetime
from typing import List, Literal, Tuple

import jwt
from fastapi import HTTPException, status
from redis.client import Redis
from sqlalchemy.exc import IntegrityError

from app.domain.models.session import UserSession
from app.domain.models.user import User
from app.domain.repositories.interfaces.auth import (
    IAuthRepository,
    JwtTokenPayload,
    JwtTokenType,
)
from app.domain.repositories.interfaces.session import ISessionRepository
from app.domain.repositories.interfaces.user import IUserRepository
from app.dto.auth import SigninDTO, SignupDTO
from app.services.interfaces.auth import IAuthService


class AuthService(IAuthService):
    """Auth service."""

    def __init__(
        self,
        cache: Redis,
        auth_repository: IAuthRepository,
        user_repository: IUserRepository,
        session_repository: ISessionRepository,
    ):
        self.cache = cache
        self.auth_repository = auth_repository
        self.user_repository = user_repository
        self.session_repository = session_repository

    def _decode_token_safely(
        self, token: str, expected_type: JwtTokenType = None
    ) -> JwtTokenPayload:
        """Decode token with proper error handling."""
        try:
            payload = self.auth_repository.decode_token(token)
        except jwt.ExpiredSignatureError as exc:
            token_type = expected_type or JwtTokenType.ACCESS
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"{token_type} has expired",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc
        except Exception as exc:
            token_type = expected_type or JwtTokenType.ACCESS
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid {token_type.value}",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        # Verify token type if expected_type is specified
        if expected_type and payload.get("type") != expected_type.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        return payload

    def _check_token_blacklist(self, jti: str) -> None:
        """Check if token is blacklisted and raise exception if it is."""
        if jti and self.cache.get(f"blacklist:{jti}"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def _validate_token_payload(
        self,
        payload: JwtTokenPayload,
        required_keys: List[Literal["sub", "sid", "type", "iat", "exp", "jti"]],
    ) -> None:
        """Validate that required keys exist in token payload."""
        for key in required_keys:
            if key not in payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Missing required key: {key}",
                    headers={"WWW-Authenticate": "Bearer"},
                )

    def _validate_session(self, session_id: str) -> UserSession:
        """Validate session exists, is active, and not expired."""
        session = self.session_repository.get_by_id(session_id)

        if not session or not session.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if session has expired
        if session.is_expired():
            self.session_repository.deactivate(session_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return session

    def _calculate_token_ttl(self, exp: int) -> int:
        """Calculate TTL for a token based on its expiration."""
        return exp - int(datetime.datetime.now(datetime.timezone.utc).timestamp())

    def _blacklist_token(self, jti: str, exp: int) -> None:
        """Add token to blacklist with appropriate TTL."""
        if jti and exp:
            ttl = self._calculate_token_ttl(exp)
            if ttl > 0:
                self.cache.setex(f"blacklist:{jti}", ttl, "1")

    def _validate_user_exists_and_active(self, user_id: str) -> User:
        """Validate user exists and is active."""
        user = self.user_repository.get_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user account",
            )

        return user

    def _create_session_and_tokens(self, user: User, host: str) -> Tuple[str, str]:
        """Create session and generate access and refresh tokens."""
        session = UserSession(
            user_id=user.id,
            host=host,
            expires_at=datetime.datetime.now(datetime.timezone.utc),
        )
        session = self.session_repository.create(session)

        # Create tokens with the actual session ID and get expiration
        (access_token, refresh_token, refresh_token_exp) = (
            self.auth_repository.create_token(
                {"sub": str(user.id), "sid": str(session.id)}
            )
        )

        # Update session expiry to match the refresh token
        session.expires_at = refresh_token_exp
        self.session_repository.update(session)

        return access_token, refresh_token

    def signup(self, host: str, dto: SignupDTO) -> Tuple[User, str, str]:
        """Register a new user."""
        hashed_password = self.auth_repository.hash_password(dto.password)

        user = User(email=dto.email, hashed_password=hashed_password)

        try:
            user = self.user_repository.create(user)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            ) from exc

        access_token, refresh_token = self._create_session_and_tokens(user, host)

        return user, access_token, refresh_token

    def signin(self, host: str, dto: SigninDTO) -> Tuple[str, str]:
        """Authenticate a user and return JWT access token and refresh token."""
        user = self.user_repository.get_by_email(dto.email)

        if not user or not self.auth_repository.verify_password(
            dto.password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return self._create_session_and_tokens(user, host)

    def authorize(self, token: str) -> JwtTokenPayload:
        """Authorize a user by token."""
        return self._decode_token_safely(token, expected_type=JwtTokenType.ACCESS)

    def get_authenticated_user(self, token: str) -> User:
        """Get authenticated user from access token."""
        payload = self.authorize(token)

        self._check_token_blacklist(payload["jti"])
        self._validate_token_payload(payload, ["sub", "sid"])
        self._validate_session(payload["sid"])

        return self._validate_user_exists_and_active(payload["sub"])

    def refresh_token(self, refresh_token: str) -> Tuple[str, str]:
        """Refresh access token using refresh token."""
        payload = self._decode_token_safely(
            refresh_token, expected_type=JwtTokenType.REFRESH
        )

        self._check_token_blacklist(payload["jti"])
        self._validate_token_payload(payload, ["sub", "sid"])

        session = self._validate_session(payload["sid"])

        self._blacklist_token(payload["jti"], payload["exp"])

        access_token, new_refresh_token, refresh_token_exp = (
            self.auth_repository.create_token(
                {"sub": payload["sub"], "sid": payload["sid"]}
            )
        )

        session.expires_at = refresh_token_exp
        self.session_repository.update(session)

        return access_token, new_refresh_token

    def signout(self, token: str) -> bool:
        """Sign out a user and revoke their session."""

        payload = self.authorize(token)

        self.session_repository.deactivate(payload["sid"])
        self._blacklist_token(payload["jti"], payload["exp"])
        return True
