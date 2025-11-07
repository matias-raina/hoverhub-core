from abc import ABC, abstractmethod
from typing import List, Optional


class IAccountService(ABC):
    """Interface para AccountService — expone los casos de uso principales.

    Nota: no se incluyen todos los métodos del servicio; sólo los más relevantes
    para ser usados por controladores/consumidores externos.
    """

    @abstractmethod
    def create_account(self, user_id: int, account_type_id: int) -> dict:
        """Crea una nueva cuenta para un usuario existente."""

    @abstractmethod
    def get_accounts_by_user(self, user_id: int) -> List[dict]:
        """Devuelve las cuentas asociadas a un usuario."""

    @abstractmethod
    def remove_account(self, account_id: int) -> bool:
        """Elimina una cuenta del sistema."""

    @abstractmethod
    def change_account_status(self, account_id: int, new_status_id: int) -> dict:
        """Actualiza el estado de una cuenta (por ejemplo activar/desactivar)."""
