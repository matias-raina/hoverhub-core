from datetime import date
from uuid import UUID

from fastapi import HTTPException, Query, status

from app.domain.models.job import Job, JobUpdate
from app.domain.repositories.interfaces.job import IJobRepository
from app.services.interfaces.job import IJobService


class JobService(IJobService):
    def __init__(self, job_repository: IJobRepository):
        self.job_repository = job_repository

    def create_job(self, job: Job) -> Job:
        """Create a new job."""
        # Ensure account_id is a UUID object (SQLModel/Pydantic might pass string)
        if isinstance(job.account_id, str):
            job.account_id = UUID(job.account_id)
        # Ensure dates are date objects (SQLModel/Pydantic might pass strings)
        if isinstance(job.start_date, str):
            job.start_date = date.fromisoformat(job.start_date)
        if isinstance(job.end_date, str):
            job.end_date = date.fromisoformat(job.end_date)
        return self.job_repository.create(job)

    def read_job(self, job_id: UUID) -> Job | None:
        """Retrieve a job by ID."""
        job = self.job_repository.read_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID {job_id} not found",
            )
        return job

    def read_jobs(self, offset: int = 0, limit: int = Query(default=100, le=100)) -> list[Job]:
        """Retrieve all jobs."""
        return self.job_repository.read_jobs(offset=offset, limit=limit)

    def update_job(self, job_id: UUID, job: JobUpdate) -> Job | None:
        """Update an existing job."""
        updated_job = self.job_repository.update(job_id, job)
        if not updated_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID {job_id} not found",
            )
        return updated_job

    def delete_job(self, job_id: UUID) -> bool:
        """Delete a job by ID."""
        success = self.job_repository.delete(job_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID {job_id} not found",
            )
        return success
