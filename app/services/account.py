from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status

from app.domain.models.account import Account
from app.domain.repositories.account import IAccountRepository
from app.domain.repositories.user import IUserRepository
from app.dto.account import CreateAccountDto
from app.services.interfaces.account import IAccountService


class AccountService(IAccountService):
    def __init__(
        self, account_repository: IAccountRepository, user_repository: IUserRepository
    ):
        self.account_repository = account_repository
        self.user_repository = user_repository

    def get_account_by_id(self, user_id: UUID, account_id: UUID) -> Optional[Account]:
        account = self.account_repository.get_by_id(account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
            )
        if account.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this account",
            )
        return account

    def create_account(self, user_id: UUID, dto: CreateAccountDto) -> Account:
        account = Account(user_id=user_id, name=dto.name, account_type=dto.account_type)
        return self.account_repository.create(account)

    def get_user_accounts(self, user_id: UUID) -> List[Account]:
        return self.account_repository.get_user_accounts(user_id)

    def update_account(self, account_id: UUID, account: Account) -> Account:
        return self.account_repository.update(account_id, account)

    def delete_account(self, user_id: UUID, account_id: UUID) -> bool:
        # Fetch the account to be deleted
        account = self.account_repository.get_by_id(account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
            )

        return self.account_repository.delete(account_id)
