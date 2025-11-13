from uuid import UUID

from fastapi import HTTPException, status

from app.domain.models.account import Account, AccountType, AccountUpdate
from app.domain.repositories.account import IAccountRepository
from app.domain.repositories.user import IUserRepository
from app.dto.account import CreateAccountDto
from app.services.interfaces.account import IAccountService


class AccountService(IAccountService):
    def __init__(self, account_repository: IAccountRepository, user_repository: IUserRepository):
        self.account_repository = account_repository
        self.user_repository = user_repository

    def get_account_by_id(self, user_id: UUID, account_id: UUID) -> Account | None:
        account = self.account_repository.get_by_id(account_id)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        if account.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this account",
            )
        return account

    def create_account(self, user_id: UUID, dto: CreateAccountDto) -> Account:
        # Users can only have one droner account and multiple employer accounts
        if dto.account_type == AccountType.DRONER:
            existing_droner_accounts = self.account_repository.get_user_accounts(
                user_id, AccountType.DRONER
            )
            if existing_droner_accounts:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User can only have one droner account",
                )
        account = Account(user_id=user_id, name=dto.name, account_type=dto.account_type)
        return self.account_repository.create(account)

    def get_user_accounts(self, user_id: UUID) -> list[Account]:
        return self.account_repository.get_user_accounts(user_id)

    def update_account(
        self, user_id: UUID, account_id: UUID, account_update: AccountUpdate
    ) -> Account:
        account = self.account_repository.get_by_id(account_id)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        if account.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this account",
            )
        return self.account_repository.update(account_id, account_update)
