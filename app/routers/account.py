from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from fastapi import Depends
from sqlmodel import Session

from app.config.dependencies import get_db, get_user_repository
from app.domain.repositories.account import AccountRepository
from app.domain.repositories.interfaces.user import IUserRepository
from app.services.account import AccountService

router = APIRouter(prefix="/accounts", tags=["Accounts"])


def get_account_service(session: Session = Depends(get_db), user_repository: IUserRepository = Depends(get_user_repository)):
    """Construye una instancia de AccountService para inyección local.

    Nota: en un proyecto más grande estas fábricas irían en `app.config.dependencies`.
    """
    repo = AccountRepository(session)
    return AccountService(repo, user_repository)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_account(user_id: str, account_type_id: int, account_service: AccountService = Depends(get_account_service)):
    """Crea una nueva cuenta para un usuario existente."""
    account = account_service.create_account(user_id, account_type_id)
    return account


@router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def get_accounts_by_user(user_id: str, account_service: AccountService = Depends(get_account_service)):
    """Obtiene todas las cuentas asociadas a un usuario."""
    return account_service.get_accounts_by_user(user_id)


@router.patch("/{account_id}/status", status_code=status.HTTP_200_OK)
async def change_account_status(account_id: str, new_status_id: int, account_service: AccountService = Depends(get_account_service)):
    """Cambia el estado de una cuenta (por ejemplo activar/desactivar)."""
    try:
        return account_service.change_account_status(account_id, new_status_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_account(account_id: str, account_service: AccountService = Depends(get_account_service)):
    """Elimina una cuenta del sistema."""
    account_service.remove_account(account_id)
    return None
