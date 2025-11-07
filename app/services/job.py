from typing import Optional

from fastapi import HTTPException, status, Query

from app.domain.models.job import Job, JobUpdate
from app.domain.repositories.interfaces.job import IJobRepository
from app.services.interfaces.job import IJobService


class JobService(IJobService):
    def __init__(self, job_repository: IJobRepository):
        self.job_repository = job_repository

    def create_job(self, job: Job) -> Job:
        """Create a new job."""
        return self.job_repository.create(job)

    def read_job(self, job_id: str) -> Optional[Job]:
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

    def update_job(self, job_id: str, job: JobUpdate) -> Optional[Job]:
        """Update an existing job."""
        updated_job = self.job_repository.update(job_id, job)
        if not updated_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID {job_id} not found",
            )
        return updated_job

    def delete_job(self, job_id: str) -> bool:
        """Delete a job by ID."""
        success = self.job_repository.delete(job_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID {job_id} not found",
            )
        return success
