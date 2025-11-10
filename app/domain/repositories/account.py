from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from app.domain.models.account import Account, AccountType, AccountUpdate
from app.domain.repositories.interfaces.account import IAccountRepository


class AccountRepository(IAccountRepository):
    """Account repository."""

    def __init__(self, session: Session):
        """Initialize the account repository."""
        self.session = session

    def create(self, account: Account) -> Account:
        """Create a new account in the database."""
        self.session.add(account)
        self.session.commit()
        self.session.refresh(account)
        return account

    def get_by_id(self, account_id: UUID) -> Optional[Account]:
        """Retrieve an account by ID."""
        return self.session.get(Account, account_id)

    def get_user_accounts(
        self, user_id: UUID, account_type: Optional[AccountType] = None
    ) -> List[Account]:
        """Retrieve all accounts for a specific user and account type."""
        statement = select(Account).where(Account.user_id == user_id)
        if account_type:
            statement = statement.where(Account.account_type == account_type)
        return list(self.session.exec(statement).all())

    def get_all(self) -> List[Account]:
        """Retrieve all accounts."""
        return list(self.session.exec(select(Account)).all())

    def update(self, account_id: UUID, account_update: AccountUpdate) -> Account:
        """Update an existing account."""
        account = self.get_by_id(account_id)
        if not account:
            raise ValueError(f"Account with ID {account_id} not found")
        account.sqlmodel_update(account_update)
        self.session.add(account)
        self.session.commit()
        self.session.refresh(account)
        return account
