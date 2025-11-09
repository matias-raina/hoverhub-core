from abc import ABC, abstractmethod

from app.domain.models.user import User
from app.dto.auth import SigninDTO, SignupDTO


class IAuthService(ABC):

    @abstractmethod
    def signup(self, dto: SignupDTO) -> User:
        pass

    @abstractmethod
    def signin(self, dto: SigninDTO) -> str:
        pass

    @abstractmethod
    def authorize(self, token: str) -> dict:
        pass

    @abstractmethod
    def get_authenticated_user(self, token: str) -> User:
        pass

    @abstractmethod
    def signout(self):
        pass
