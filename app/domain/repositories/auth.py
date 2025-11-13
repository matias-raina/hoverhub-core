import uuid
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.config.settings import Settings
from app.domain.repositories.interfaces.auth import IAuthRepository, JwtTokenType


class AuthRepository(IAuthRepository):
    """Auth repository."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.hasher = PasswordHash.recommended()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.hasher.verify(plain_password, hashed_password)

    def hash_password(self, plain_password: str) -> str:
        return self.hasher.hash(plain_password)

    def decode_token(self, token: str) -> dict:
        """Decode a token and return raw payload dictionary."""
        return jwt.decode(token, self.settings.secret_key, algorithms=[self.settings.algorithm])  # type: ignore[no-any-return]

    def create_token(self, data: dict) -> tuple[str, str, datetime]:
        iat = datetime.now(UTC)

        access_token_jti = str(uuid.uuid4())
        refresh_token_jti = str(uuid.uuid4())

        access_token_exp = iat + timedelta(minutes=self.settings.access_token_expire_minutes)
        refresh_token_exp = iat + timedelta(minutes=self.settings.refresh_token_expire_minutes)

        access_token = jwt.encode(
            {
                **data,
                "jti": access_token_jti,
                "type": JwtTokenType.ACCESS,
                "iat": iat,
                "exp": access_token_exp,
            },
            self.settings.secret_key,
            algorithm=self.settings.algorithm,
        )

        refresh_token = jwt.encode(
            {
                **data,
                "jti": refresh_token_jti,
                "type": JwtTokenType.REFRESH,
                "iat": iat,
                "exp": refresh_token_exp,
            },
            self.settings.secret_key,
            algorithm=self.settings.algorithm,
        )

        return (access_token, refresh_token, refresh_token_exp)
