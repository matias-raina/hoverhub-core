from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.config.settings import Settings
from app.domain.repositories.interfaces.auth import IAuthRepository


class AuthRepository(IAuthRepository):
    def __init__(self, settings: Settings):
        self.settings = settings

        self.hasher = PasswordHash.recommended()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.hasher.verify(plain_password, hashed_password)

    def hash_password(self, plain_password: str) -> str:
        return self.hasher.hash(plain_password)

    def verify_token(self, token: str) -> dict:
        return jwt.decode(
            token, self.settings.secret_key, algorithms=[self.settings.algorithm]
        )

    def create_token(self, data: dict) -> str:
        return jwt.encode(
            {
                **data,
                "exp": datetime.now(timezone.utc)
                + timedelta(minutes=self.settings.access_token_expire_minutes),
            },
            self.settings.secret_key,
            algorithm=self.settings.algorithm,
        )

    def decode_token(self, token: str) -> dict:
        return jwt.decode(
            token, self.settings.secret_key, algorithms=[self.settings.algorithm]
        )
