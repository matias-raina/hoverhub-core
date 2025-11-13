from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from app.domain.models.job import Job
from app.dto.job import CreateJobDto, UpdateJobDto


class IJobService(ABC):
    @abstractmethod
    def create_job(self, account_id: UUID, dto: CreateJobDto) -> Job:
        """Create a new job."""

    @abstractmethod
    def get_by_id(self, account_id: UUID, job_id: UUID) -> Job | None:
        """Retrieve a job by ID."""

    @abstractmethod
    def get_all(self, offset: int, limit: int) -> Sequence[Job]:
        """Retrieve all jobs."""

    @abstractmethod
    def update_job(self, account_id: UUID, job_id: UUID, dto: UpdateJobDto) -> Job:
        """Update an existing job."""

    @abstractmethod
    def delete_job(self, account_id: UUID, job_id: UUID) -> bool:
        """Delete a job by ID."""
