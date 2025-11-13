from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.config.dependencies import AuthenticatedAccountDep, JobServiceDep
from app.dto.job import CreateJobDto, UpdateJobDto

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_job(
    authenticated_account: AuthenticatedAccountDep,
    dto: CreateJobDto,
    job_service: JobServiceDep,
):
    """
    Create a new job.

    Args:
        authenticated_account: The authenticated account from authentication
        dto: The job data to create
        job_service: Injected job service

    Returns:
        The created job information
    """
    job = job_service.create_job(authenticated_account.id, dto)
    return {
        "id": job.id,
        "account_id": job.account_id,
        "title": job.title,
        "description": job.description,
        "budget": job.budget,
        "location": job.location,
        "start_date": job.start_date,
        "end_date": job.end_date,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }


@router.get("/{job_id}", status_code=status.HTTP_200_OK)
async def get_job(
    authenticated_account: AuthenticatedAccountDep,
    job_id: UUID,
    job_service: JobServiceDep,
):
    """
    Get a job by ID.

    Args:
        authenticated_account: The authenticated account from authentication
        job_id: The ID of the job to retrieve
        job_service: Injected job service

    Returns:
        Job information
    """
    job = job_service.get_by_id(authenticated_account.id, job_id)
    return {
        "id": job.id,
        "account_id": job.account_id,
        "title": job.title,
        "description": job.description,
        "budget": job.budget,
        "location": job.location,
        "start_date": job.start_date,
        "end_date": job.end_date,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }


@router.get("/", status_code=status.HTTP_200_OK)
async def list_jobs(
    _: AuthenticatedAccountDep,
    job_service: JobServiceDep,
    offset: Annotated[int, Query(ge=0, description="Number of items to skip")] = 0,
    limit: Annotated[
        int, Query(ge=1, le=100, description="Maximum number of items to return")
    ] = 100,
):
    """
    List all jobs with pagination.

    Results are ordered by creation date (newest first).

    Args:
        _: The authenticated account from authentication
        job_service: Injected job service
        offset: The number of items to skip before starting to collect the result set (min: 0)
        limit: The maximum number of items to return (min: 1, max: 100)

    Returns:
        A list of jobs ordered by creation date (newest first)
    """

    jobs = job_service.get_all(offset=offset, limit=limit)
    return [
        {
            "id": job.id,
            "account_id": job.account_id,
            "title": job.title,
            "description": job.description,
            "budget": job.budget,
            "location": job.location,
            "start_date": job.start_date,
            "end_date": job.end_date,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
        }
        for job in jobs
    ]


@router.put("/{job_id}", status_code=status.HTTP_200_OK)
async def update_job(
    authenticated_account: AuthenticatedAccountDep,
    job_id: UUID,
    dto: UpdateJobDto,
    job_service: JobServiceDep,
):
    """
    Update a job by ID.

    Args:
        authenticated_account: The authenticated account from authentication
        job_id: The ID of the job to update
        dto: The updated job data
        job_service: Injected job service

    Returns:
        The updated job information
    """
    job = job_service.update_job(authenticated_account.id, job_id, dto)
    return {
        "id": job.id,
        "account_id": job.account_id,
        "title": job.title,
        "description": job.description,
        "budget": job.budget,
        "location": job.location,
        "start_date": job.start_date,
        "end_date": job.end_date,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    authenticated_account: AuthenticatedAccountDep,
    job_id: UUID,
    job_service: JobServiceDep,
):
    """
    Delete a job by ID.

    Args:
        authenticated_account: The authenticated account from authentication
        job_id: The ID of the job to delete
        job_service: Injected job service
    """
    job_service.delete_job(authenticated_account.id, job_id)
