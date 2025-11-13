from typing import Optional, Sequence
from uuid import UUID

from fastapi import HTTPException, status

from app.domain.models.job import Job, JobUpdate
from app.domain.repositories.interfaces.job import IJobRepository
from app.services.interfaces.job import IJobService
from app.dto.job import CreateJobDto, UpdateJobDto


class JobService(IJobService):
    def __init__(self, job_repository: IJobRepository):
        self.job_repository = job_repository

    def create_job(self, account_id: UUID, dto: CreateJobDto) -> Job:
        """Create a new job."""
        job = Job(
            account_id=account_id,
            title=dto.title,
            description=dto.description,
            budget=dto.budget,
            location=dto.location,
            start_date=dto.start_date,
            end_date=dto.end_date,
        )
        return self.job_repository.create(job)

    def get_by_id(self, account_id: UUID, job_id: UUID) -> Optional[Job]:
        """Retrieve a job by ID."""
        job = self.job_repository.get_by_id(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
            )
        if job.account_id != account_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this job",
            )
        return job

    def get_all(
        self, offset: int = 0, limit: int = 100
    ) -> Sequence[Job]:
        """Retrieve all jobs."""
        return self.job_repository.get_all(offset=offset, limit=limit)

    def update_job(self, account_id: UUID, job_id: UUID, dto: UpdateJobDto) -> Job:
        """Update an existing job."""
        job = self.job_repository.get_by_id(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
            )
        if job.account_id != account_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update this job",
            )

        job_update = JobUpdate(**dto.model_dump(exclude_unset=True))
        return self.job_repository.update(job_id, job_update)

    def delete_job(self, account_id: UUID, job_id: UUID) -> bool:
        """Delete a job by ID."""
        job = self.job_repository.get_by_id(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
            )
        if job.account_id != account_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to delete this job",
            )
        return self.job_repository.delete(job_id)
