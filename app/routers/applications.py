from uuid import UUID

from fastapi import APIRouter, status

from app.config.dependencies import (
    ApplicationServiceDep,
    AuthenticatedAccountDep,
)

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get("/", status_code=status.HTTP_200_OK)
async def list_applications_for_account(
    authenticated_account: AuthenticatedAccountDep,
    application_service: ApplicationServiceDep,
):
    """
    List all applications submitted by the authenticated DRONER account.

    Only DRONER accounts can access this endpoint.
    """
    applications = application_service.list_applications_for_account(authenticated_account.id)
    return [
        {
            "id": app.id,
            "job_id": app.job_id,
            "account_id": app.account_id,
            "status": app.status,
            "message": app.message,
            "created_at": app.created_at,
            "updated_at": app.updated_at,
        }
        for app in applications
    ]


@router.get("/{application_id}", status_code=status.HTTP_200_OK)
async def get_application(
    application_id: UUID,
    authenticated_account: AuthenticatedAccountDep,
    application_service: ApplicationServiceDep,
):
    """
    Get a specific application by ID.

    Accessible by:
    - The DRONER account that submitted the application
    - The EMPLOYER account that owns the job
    """
    application = application_service.get_application(authenticated_account.id, application_id)
    return {
        "id": application.id,
        "job_id": application.job_id,
        "account_id": application.account_id,
        "status": application.status,
        "message": application.message,
        "created_at": application.created_at,
        "updated_at": application.updated_at,
    }


@router.post("/{application_id}/withdraw", status_code=status.HTTP_200_OK)
async def withdraw_application(
    application_id: UUID,
    authenticated_account: AuthenticatedAccountDep,
    application_service: ApplicationServiceDep,
):
    """
    Withdraw an application (set status to WITHDRAWN).

    Only the DRONER account that submitted the application can withdraw it.
    """
    application = application_service.withdraw_application(authenticated_account.id, application_id)
    return {
        "id": application.id,
        "job_id": application.job_id,
        "account_id": application.account_id,
        "status": application.status,
        "message": application.message,
        "created_at": application.created_at,
        "updated_at": application.updated_at,
    }


@router.post("/{application_id}/accept", status_code=status.HTTP_200_OK)
async def accept_application(
    application_id: UUID,
    authenticated_account: AuthenticatedAccountDep,
    application_service: ApplicationServiceDep,
):
    """
    Accept an application (set status to ACCEPTED).

    Only the EMPLOYER account that owns the job can accept applications.
    """
    application = application_service.accept_application(authenticated_account.id, application_id)
    return {
        "id": application.id,
        "job_id": application.job_id,
        "account_id": application.account_id,
        "status": application.status,
        "message": application.message,
        "created_at": application.created_at,
        "updated_at": application.updated_at,
    }


@router.post("/{application_id}/reject", status_code=status.HTTP_200_OK)
async def reject_application(
    application_id: UUID,
    authenticated_account: AuthenticatedAccountDep,
    application_service: ApplicationServiceDep,
):
    """
    Reject an application (set status to REJECTED).

    Only the EMPLOYER account that owns the job can reject applications.
    """
    application = application_service.reject_application(authenticated_account.id, application_id)
    return {
        "id": application.id,
        "job_id": application.job_id,
        "account_id": application.account_id,
        "status": application.status,
        "message": application.message,
        "created_at": application.created_at,
        "updated_at": application.updated_at,
    }
