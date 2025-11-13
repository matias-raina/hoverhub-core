from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models.account import Account, AccountUpdate
from app.dto.account import CreateAccountDto


class IAccountService(ABC):
    @abstractmethod
    def get_account_by_id(self, user_id: UUID, account_id: UUID) -> Account | None:
        """Get an account by ID."""

    @abstractmethod
    def create_account(self, user_id: UUID, dto: CreateAccountDto) -> Account:
        """Create a new account for an existing user."""

    @abstractmethod
    def get_user_accounts(self, user_id: UUID) -> list[Account]:
        """Get the accounts associated with a user."""

    @abstractmethod
    def update_account(
        self, user_id: UUID, account_id: UUID, account_update: AccountUpdate
    ) -> Account:
        """Update an existing account."""
