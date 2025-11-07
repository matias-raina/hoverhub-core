from typing import Optional

from sqlmodel import Session, select

from app.domain.models.account import Account
from app.domain.repositories.interfaces.account import IAccountRepository


class AccountRepository(IAccountRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(self, account: Account) -> Account:
        """Create a new account in the database."""
        self.session.add(account)
        self.session.commit()
        self.session.refresh(account)
        return account

    def get_by_email(self, email: str) -> Optional[Account]:
        """Retrieve an account by email."""
        statement = select(Account).where(Account.email == email)
        return self.session.exec(statement).first()

    def get_by_id(self, account_id: str) -> Optional[Account]:
        """Retrieve an account by ID."""
        return self.session.get(Account, account_id)

    def get_all(self) -> list[Account]:
        """Retrieve all accounts."""
        statement = select(Account)
        return self.session.exec(statement).all()

    def update(self, account: Account) -> Account:
        """Update an existing account."""
        self.session.add(account)
        self.session.commit()
        self.session.refresh(account)
        return account

    def delete(self, account_id: str) -> bool:
        """Delete an account by ID."""
        account = self.get_by_id(account_id)
        if account:
            self.session.delete(account)
            self.session.commit()
            return True
        return False
