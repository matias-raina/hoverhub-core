from uuid import UUID

from fastapi import APIRouter, status

from app.config.dependencies import ApplicationServiceDep, AuthenticatedUserDep
from app.dto.application import CreateApplicationDto, UpdateApplicationStatusDto

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("/jobs/{job_id}", status_code=status.HTTP_201_CREATED)
async def apply_to_job(
    job_id: UUID,
    dto: CreateApplicationDto,
    authenticated_user: AuthenticatedUserDep,
    application_service: ApplicationServiceDep,
):
    application = application_service.apply_to_job(authenticated_user.id, job_id, dto)
    return {
        "id": application.id,
        "job_id": application.job_id,
        "account_id": application.account_id,
        "status": application.status,
        "message": application.message,
        "created_at": application.created_at,
        "updated_at": application.updated_at,
    }


@router.get("/jobs/{job_id}", status_code=status.HTTP_200_OK)
async def list_applications_for_job(
    job_id: UUID,
    authenticated_user: AuthenticatedUserDep,
    application_service: ApplicationServiceDep,
):
    applications = application_service.list_applications_for_job(
        authenticated_user.id, job_id
    )
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


@router.get("/", status_code=status.HTTP_200_OK)
async def list_applications_for_user(
    authenticated_user: AuthenticatedUserDep,
    application_service: ApplicationServiceDep,
):
    applications = application_service.list_applications_for_user(authenticated_user.id)
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


@router.patch("/{application_id}", status_code=status.HTTP_200_OK)
async def update_application_status(
    application_id: UUID,
    dto: UpdateApplicationStatusDto,
    authenticated_user: AuthenticatedUserDep,
    application_service: ApplicationServiceDep,
):
    updated = application_service.update_application_status(
        authenticated_user.id, application_id, dto
    )
    return {
        "id": updated.id,
        "job_id": updated.job_id,
        "account_id": updated.account_id,
        "status": updated.status,
        "message": updated.message,
        "created_at": updated.created_at,
        "updated_at": updated.updated_at,
    }


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: UUID,
    authenticated_user: AuthenticatedUserDep,
    application_service: ApplicationServiceDep,
):
    application_service.delete_application(authenticated_user.id, application_id)
