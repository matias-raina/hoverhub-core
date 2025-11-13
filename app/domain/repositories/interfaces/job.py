from abc import ABC, abstractmethod
from typing import Optional, Sequence
from uuid import UUID

from app.domain.models.job import Job, JobUpdate


class IJobRepository(ABC):
    @abstractmethod
    def create(self, job: Job) -> Job:
        """Create a new job entry in the database."""

    @abstractmethod
    def get_by_id(self, job_id: UUID) -> Optional[Job]:
        """Retrieve a job entry by ID."""

    @abstractmethod
    def get_all(self, offset: int, limit: int) -> Sequence[Job]:
        """Retrieve all job entries."""

    @abstractmethod
    def update(self, job_id: UUID, job: JobUpdate) -> Optional[Job]:
        """Update an existing job entry."""

    @abstractmethod
    def delete(self, job_id: UUID) -> bool:
        """Delete a job entry by ID."""
