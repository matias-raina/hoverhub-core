from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models.account import Account, AccountType, AccountUpdate


class IAccountRepository(ABC):
    """Account repository interface."""

    @abstractmethod
    def create(self, account: Account) -> Account:
        """Create a new account in the database."""

    @abstractmethod
    def get_by_id(self, account_id: UUID) -> Account | None:
        """Retrieve an account by ID."""

    @abstractmethod
    def get_user_accounts(
        self, user_id: UUID, account_type: AccountType | None = None
    ) -> list[Account]:
        """Retrieve all accounts for a specific user and account type."""

    @abstractmethod
    def get_all(self) -> list[Account]:
        """Retrieve all accounts."""

    @abstractmethod
    def update(self, account_id: UUID, account_update: AccountUpdate) -> Account:
        """Update an existing account."""
