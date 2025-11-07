from abc import ABC, abstractmethod
from typing import Optional
from app.domain.models.job import Job, JobUpdate


class IJobService(ABC):
    @abstractmethod
    def create_job(self, job: Job) -> Job:
        """Create a new job."""

    @abstractmethod
    def read_job(self, job_id: str) -> Optional[Job]:
        """Retrieve a job by ID."""

    @abstractmethod
    def read_jobs(self, offset: int, limit: int) -> list[Job]:
        """Retrieve all jobs."""

    @abstractmethod
    def update_job(self, job_id: str, job: JobUpdate) -> Optional[Job]:
        """Update an existing job."""

    @abstractmethod
    def delete_job(self, job_id: str) -> bool:
        """Delete a job by ID."""
