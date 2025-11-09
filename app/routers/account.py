from uuid import UUID

from fastapi import APIRouter, status

from app.config.dependencies import AccountServiceDep, AuthenticatedUserDep
from app.dto.account import CreateAccountDto

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_account(
    authenticated_user: AuthenticatedUserDep,
    dto: CreateAccountDto,
    account_service: AccountServiceDep,
):
    return account_service.create_account(authenticated_user.id, dto)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user_accounts(
    authenticated_user: AuthenticatedUserDep,
    account_service: AccountServiceDep,
):
    return account_service.get_user_accounts(authenticated_user.id)


@router.get("/{account_id}", status_code=status.HTTP_200_OK)
async def get_account(
    authenticated_user: AuthenticatedUserDep,
    account_service: AccountServiceDep,
    account_id: UUID,
):
    return account_service.get_account_by_id(authenticated_user.id, account_id)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_account(
    authenticated_user: AuthenticatedUserDep,
    account_service: AccountServiceDep,
    account_id: UUID,
):
    account_service.delete_account(authenticated_user.id, account_id)
    return None
