from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.models.account import Account
from app.dto.account import CreateAccountDto


class IAccountService(ABC):

    @abstractmethod
    def get_account_by_id(self, user_id: UUID, account_id: UUID) -> Optional[Account]:
        """Get an account by ID."""

    @abstractmethod
    def create_account(self, user_id: UUID, dto: CreateAccountDto) -> Account:
        """Create a new account for an existing user."""

    @abstractmethod
    def get_user_accounts(self, user_id: UUID) -> List[Account]:
        """Get the accounts associated with a user."""

    @abstractmethod
    def update_account(self, account_id: UUID, account: Account) -> Account:
        """Update an existing account."""

    @abstractmethod
    def delete_account(self, user_id: UUID, account_id: UUID) -> bool:
        """Delete an existing account. Validates that the user can only delete accounts from their domain."""
