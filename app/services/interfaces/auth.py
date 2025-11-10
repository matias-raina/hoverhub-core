from abc import ABC, abstractmethod
from typing import Tuple

from app.domain.models.user import User
from app.dto.auth import SigninDTO, SignupDTO


class IAuthService(ABC):

    @abstractmethod
    def signup(self, host: str, dto: SignupDTO) -> Tuple[User, str, str]:
        pass

    @abstractmethod
    def signin(self, host: str, dto: SigninDTO) -> Tuple[str, str]:
        pass

    @abstractmethod
    def authorize(self, token: str) -> dict:
        pass

    @abstractmethod
    def get_authenticated_user(self, token: str) -> User:
        pass

    @abstractmethod
    def refresh_token(self, refresh_token: str) -> Tuple[str, str]:
        pass

    @abstractmethod
    def signout(self, token: str) -> bool:
        pass
