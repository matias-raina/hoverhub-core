from collections.abc import Sequence
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

    def get_by_id(self, account_id: UUID) -> Account | None:
        """Retrieve an account by ID."""
        return self.session.get(Account, account_id)

    def get_user_accounts(
        self, user_id: UUID, account_type: AccountType | None = None
    ) -> Sequence[Account]:
        """Retrieve all accounts for a specific user and account type."""
        statement = select(Account).where(Account.user_id == user_id)
        if account_type:
            statement = statement.where(Account.account_type == account_type)
        return self.session.exec(statement).all()

    def get_all(self) -> Sequence[Account]:
        """Retrieve all accounts."""
        return self.session.exec(select(Account)).all()

    def update(self, account_id: UUID, account: AccountUpdate) -> Account | None:
        """Update an existing account."""
        db_account = self.get_by_id(account_id)
        if not db_account:
            return None
        account_data = account.model_dump(exclude_unset=True)
        db_account.sqlmodel_update(account_data)
        self.session.add(db_account)
        self.session.commit()
        self.session.refresh(db_account)
        return db_account
