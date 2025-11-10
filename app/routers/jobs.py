from uuid import UUID

from fastapi import APIRouter, status

from app.config.dependencies import JobServiceDep
from app.domain.models.job import Job, JobUpdate

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: Job,
    job_service: JobServiceDep,
):
    """
    Create a new job.

    Args:
        job_data: The job data to create
        job_service: Injected job service

    Returns:
        The created job information
    """
    job = job_service.create_job(job_data)
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
    job_id: UUID,
    job_service: JobServiceDep,
):
    """
    Get a job by ID.

    Args:
        job_id: The ID of the job to retrieve
        job_service: Injected job service

    Returns:
        Job information
    """
    job = job_service.read_job(job_id)
    return {
        "id": job.id,
        "account_id": job.account_id,
        "title": job.title,
        "description": job.description,
        "budget": job.budget,
        "location": job.location,
        "start_date": job.start_date,
        "end_date": job.end_date.isoformat(),
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
    }


@router.get("/", status_code=status.HTTP_200_OK)
async def list_jobs(
    job_service: JobServiceDep,
    offset: int = 0,
    limit: int = 100,
):
    """
    List all jobs with pagination.

    Args:
        job_service: Injected job service
        offset: The number of items to skip before starting to collect the result set
        limit: The maximum number of items to return

    Returns:
        A list of jobs
    """
    jobs = job_service.read_jobs(offset=offset, limit=limit)
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
    job_id: UUID,
    job_data: JobUpdate,
    job_service: JobServiceDep,
):
    """
    Update a job by ID.

    Args:
        job_id: The ID of the job to update
        job_data: The updated job data
        job_service: Injected job service

    Returns:
        The updated job information
    """
    job = job_service.update_job(job_id, job_data)
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
    job_id: UUID,
    job_service: JobServiceDep,
):
    """
    Delete a job by ID.

    Args:
        job_id: The ID of the job to delete
        job_service: Injected job service
    """
    job_service.delete_job(job_id)
