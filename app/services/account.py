from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status

from app.domain.models.user import User
from app.domain.models.account import Account

from app.services.interfaces.account import IAccountService
from app.domain.repositories.user import IUserRepository
from app.domain.repositories.account import IAccountRepository


class AccountService(IAccountService):
    def __init__(self, account_repository: IAccountRepository, user_repository: IUserRepository):
        """
        account_repository: interfaz o clase encargada de persistencia de cuentas
        user_repository: interfaz o clase encargada de persistencia de usuarios
        """
        self.account_repository = account_repository
        self.user_repository = user_repository

    def create_account(self, user_id: int, account_type_id: int) -> Account:
        """Crea una nueva cuenta para un usuario existente."""
        user = self._get_user_or_404(user_id=user_id)

        account = {
            "user_id": user_id,
            "account_type_id": account_type_id,
            "account_status_type_id": 1,  # p.ej., 'active' por defecto
            "created_at": datetime.now(),
        }

        return self.account_repository.save(account)

    def get_accounts_by_user(self, user_id: int) -> List[Account]:
        """Obtiene todas las cuentas asociadas a un usuario."""
        return self.account_repository.find_by_user(user_id)

    def change_account_status(self, account_id: int, new_status_id: int) -> Account:
        """Actualiza el estado de una cuenta."""
        account = self._get_account_or_404(account_id=account_id)

        account["account_status_type_id"] = new_status_id
        self.account_repository.update(account)
        return account

    def deactivate_account(self, account_id: int) -> Account:
        """Marca una cuenta como inactiva."""
        return self.change_account_status(account_id, new_status_id=2)  # p.ej., 'inactive'

    def user_has_account_type(self, user_id: int, account_type_id: int) -> bool:
        """Verifica si el usuario ya posee una cuenta de cierto tipo."""
        accounts = self.account_repository.find_by_user(user_id)
        return any(a["account_type_id"] == account_type_id for a in accounts)

    def is_account_active(self, account_id: int) -> bool:
        """Verifica si una cuenta está activa."""
        account = self.account_repository.get_by_id(account_id)
        return account and account["account_status_type_id"] == 1

    def remove_account(self, account_id: int) -> bool:
        """Elimina una cuenta del sistema."""
        account = self._get_account_or_404(account_id=account_id)

        self.account_repository.delete(account_id)
        return True

    def _get_user_or_404(self, user_id: Optional[int] = None, email: Optional[str] = None) -> User:
        if user_id is None and email is None:
            raise ValueError("Either 'user_id' or 'email' must be provided")

        if email is not None:
            user = self.user_repository.get_by_email(email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with email {email} not found"
                )
            return user

        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        return user

    def _get_account_or_404(self, account_id: Optional[int] = None, email: Optional[str] = None) -> Account:
        from app.utils.helpers import get_account_or_404
        return get_account_or_404(
            account_repository=self.account_repository,
            account_id=account_id,
            email=email
        )
