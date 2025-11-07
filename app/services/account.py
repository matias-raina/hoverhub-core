from datetime import datetime
from typing import List, Optional

from app.domain.models.user import User
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

    def create_account(self, user_id: int, account_type_id: int) -> dict:
        """Crea una nueva cuenta para un usuario existente."""
        user = self._get_user_or_404(user_id=user_id)

        account = {
            "user_id": user_id,
            "account_type_id": account_type_id,
            "account_status_type_id": 1,  # p.ej., 'active' por defecto
            "created_at": datetime.now(),
        }

        return self.account_repository.save(account)

    def deactivate_account(self, account_id: int):
        """Marca una cuenta como inactiva."""
        account = self.account_repository.get_by_id(account_id)
        if not account:
            raise ValueError("Account not found")

        account["account_status_type_id"] = 2  # p.ej., 'inactive'
        self.account_repository.update(account)
        return account

    def get_accounts_by_user(self, user_id: int) -> List[dict]:
        """Obtiene todas las cuentas asociadas a un usuario."""
        return self.account_repository.find_by_user(user_id)

    def change_account_status(self, account_id: int, new_status_id: int):
        """Actualiza el estado de una cuenta."""
        account = self.account_repository.get_by_id(account_id)
        if not account:
            raise ValueError("Account not found")

        account["account_status_type_id"] = new_status_id
        self.account_repository.update(account)
        return account

    def user_has_account_type(self, user_id: int, account_type_id: int) -> bool:
        """Verifica si el usuario ya posee una cuenta de cierto tipo."""
        accounts = self.account_repository.find_by_user(user_id)
        return any(a["account_type_id"] == account_type_id for a in accounts)

    def is_account_active(self, account_id: int) -> bool:
        """Verifica si una cuenta está activa."""
        account = self.account_repository.get_by_id(account_id)
        return account and account["account_status_type_id"] == 1

    def remove_account(self, account_id: int):
        """Elimina una cuenta del sistema."""
        account = self.account_repository.get_by_id(account_id)
        if not account:
            raise ValueError("Account not found")
        self.account_repository.delete(account_id)
        return True
    
    def _get_user_or_404(self, user_id: Optional[int] = None, email: Optional[str] = None) -> User:
        from app.utils.helpers import get_user_or_404
        return get_user_or_404(user_repository=self.user_repository, user_id=user_id, email=email)