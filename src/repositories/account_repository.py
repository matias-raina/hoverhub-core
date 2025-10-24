from sqlalchemy.orm import Session
from typing import Optional, List
from src.models.account import Account
from src.repositories.base_repository import BaseRepository


class AccountRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = Account

    def get_account_by_id(self, account_id: int) -> Optional[Account]:
        return self.get(self.model, account_id)

    def get_accounts_by_user_id(self, user_id: int) -> List[Account]:
        return self.db_session.query(self.model).filter(self.model.user_id == user_id).all()

    def get_account_by_user_and_type(self, user_id: int, account_type_id: int) -> Optional[Account]:
        return self.db_session.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.account_type_id == account_type_id
        ).first()

    def create_account(self, account_data: dict) -> Account:
        account = Account(**account_data)
        return self.add(account)

    def update_account(self, account_id: int, account_data: dict) -> Optional[Account]:
        account = self.get(self.model, account_id)
        if account:
            for key, value in account_data.items():
                if hasattr(account, key):
                    setattr(account, key, value)
            self.db_session.commit()
            return account
        return None

    def delete_account(self, account_id: int) -> bool:
        account = self.get(self.model, account_id)
        if account:
            self.delete(account)
            return True
        return False

    def get_all_accounts(self):
        return self.get_all(self.model)
