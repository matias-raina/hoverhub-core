from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models.job import Job, JobUpdate


class IJobService(ABC):
    @abstractmethod
    def create_job(self, job: Job) -> Job:
        """Create a new job."""

    @abstractmethod
    def read_job(self, job_id: UUID) -> Job | None:
        """Retrieve a job by ID."""

    @abstractmethod
    def read_jobs(self, offset: int, limit: int) -> list[Job]:
        """Retrieve all jobs."""

    @abstractmethod
    def update_job(self, job_id: UUID, job: JobUpdate) -> Job | None:
        """Update an existing job."""

    @abstractmethod
    def delete_job(self, job_id: UUID) -> bool:
        """Delete a job by ID."""
