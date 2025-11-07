from abc import ABC, abstractmethod
from typing import Optional

from app.domain.models.account import Account


class IAccountRepository(ABC):
    @abstractmethod
    def create(self, account: Account) -> Account:
        """Create a new account in the database."""

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Account]:
        """Retrieve an account by email."""

    @abstractmethod
    def get_by_id(self, account_id: str) -> Optional[Account]:
        """Retrieve an account by ID."""

    @abstractmethod
    def get_all(self) -> list[Account]:
        """Retrieve all accounts."""

    @abstractmethod
    def update(self, account: Account) -> Account:
        """Update an existing account."""

    @abstractmethod
    def delete(self, account_id: str) -> bool:
        """Delete an account by ID."""
