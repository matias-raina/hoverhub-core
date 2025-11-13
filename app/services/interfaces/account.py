from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from app.domain.models.account import Account
from app.dto.account import CreateAccountDto, UpdateAccountDto


class IAccountService(ABC):
    @abstractmethod
    def get_account_by_id(self, user_id: UUID, account_id: UUID) -> Account:
        """Get an account by ID."""

    @abstractmethod
    def create_account(self, user_id: UUID, dto: CreateAccountDto) -> Account:
        """Create a new account for an existing user."""

    @abstractmethod
    def get_user_accounts(self, user_id: UUID) -> Sequence[Account]:
        """Get the accounts associated with a user."""

    @abstractmethod
    def update_account(self, user_id: UUID, account_id: UUID, dto: UpdateAccountDto) -> Account:
        """Update an existing account."""
