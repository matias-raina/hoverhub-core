from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.config.dependencies import AccountServiceDep, AuthenticatedUserDep
from app.dto.account import CreateAccountDto, UpdateAccountDto

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_account(
    authenticated_user: AuthenticatedUserDep,
    dto: CreateAccountDto,
    account_service: AccountServiceDep,
):
    """
    Create a new account for the authenticated user.

    Args:
        authenticated_user: Current authenticated user (injected from JWT)
        dto: Account creation data
        account_service: Injected account service

    Returns:
        The created account information
    """
    account = account_service.create_account(authenticated_user.id, dto)
    return {
        "id": account.id,
        "user_id": account.user_id,
        "name": account.name,
        "account_type": account.account_type.value,
        "is_active": account.is_active,
        "created_at": account.created_at,
        "updated_at": account.updated_at,
    }


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user_accounts(
    authenticated_user: AuthenticatedUserDep,
    account_service: AccountServiceDep,
):
    """
    Get all accounts for the authenticated user.

    Args:
        authenticated_user: Current authenticated user (injected from JWT)
        account_service: Injected account service

    Returns:
        List of user accounts
    """
    accounts = account_service.get_user_accounts(authenticated_user.id)
    return [
        {
            "id": account.id,
            "user_id": account.user_id,
            "name": account.name,
            "account_type": account.account_type.value,
            "is_active": account.is_active,
            "created_at": account.created_at,
            "updated_at": account.updated_at,
        }
        for account in accounts
    ]


@router.get("/{account_id}", status_code=status.HTTP_200_OK)
async def get_account(
    authenticated_user: AuthenticatedUserDep,
    account_service: AccountServiceDep,
    account_id: UUID,
):
    """
    Get a specific account by ID.

    Args:
        authenticated_user: Current authenticated user (injected from JWT)
        account_service: Injected account service
        account_id: The ID of the account to retrieve

    Returns:
        Account information
    """
    account = account_service.get_account_by_id(authenticated_user.id, account_id)
    return {
        "id": account.id,
        "user_id": account.user_id,
        "name": account.name,
        "account_type": account.account_type.value,
        "is_active": account.is_active,
        "created_at": account.created_at,
        "updated_at": account.updated_at,
    }


@router.put("/{account_id}", status_code=status.HTTP_200_OK)
async def update_account(
    authenticated_user: AuthenticatedUserDep,
    account_service: AccountServiceDep,
    account_id: UUID,
    dto: UpdateAccountDto,
):
    """
    Update a specific account by ID.
    """
    account = account_service.update_account(authenticated_user.id, account_id, dto)
    return {
        "id": account.id,
        "user_id": account.user_id,
        "name": account.name,
        "account_type": account.account_type.value,
        "is_active": account.is_active,
        "created_at": account.created_at,
        "updated_at": account.updated_at,
    }
