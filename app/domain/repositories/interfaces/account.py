from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.models.account import Account


class IAccountRepository(ABC):
    @abstractmethod
    def create(self, account: Account) -> Account:
        """Create a new account in the database."""

    @abstractmethod
    def get_by_id(self, account_id: UUID) -> Optional[Account]:
        """Retrieve an account by ID."""

    @abstractmethod
    def get_user_accounts(self, user_id: UUID) -> list[Account]:
        """Retrieve all accounts for a specific user."""

    @abstractmethod
    def get_all(self) -> list[Account]:
        """Retrieve all accounts."""

    @abstractmethod
    def update(self, account: Account) -> Account:
        """Update an existing account."""

    @abstractmethod
    def delete(self, account_id: UUID) -> bool:
        """Delete an account by ID."""
