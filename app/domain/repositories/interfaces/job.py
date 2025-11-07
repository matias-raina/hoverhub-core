from abc import ABC, abstractmethod
from typing import Optional
from app.domain.models.job import Job, JobUpdate
from fastapi import Query


class IJobRepository(ABC):
    @abstractmethod
    def create(self, job: Job) -> Job:
        """Create a new job entry in the database."""

    @abstractmethod
    def read_job(self, job_id: str) -> Optional[Job]:
        """Retrieve a job entry by ID."""

    @abstractmethod
    def read_jobs(self, offset: int, limit: int) -> list[Job]:
        """Retrieve all job entries."""

    @abstractmethod
    def update(self, job_id: str, job: JobUpdate) -> Job:
        """Update an existing job entry."""

    @abstractmethod
    def delete(self, job_id: str) -> bool:
        """Delete a job entry by ID."""
