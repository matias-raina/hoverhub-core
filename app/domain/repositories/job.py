from typing import Optional
from sqlmodel import Session, select
from app.domain.models.job import Job, JobUpdate
from app.domain.repositories.interfaces.job import IJobRepository
from fastapi import Query


class JobRepository(IJobRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(self, job: Job) -> Job:
        """Create a new job entry in the database."""
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job

    def read_job(self, job_id: str) -> Optional[Job]:
        """Retrieve a job entry by ID."""
        return self.session.get(Job, job_id)

    def read_jobs(self, offset: int = 0, limit: int = Query(default=100, le=100)) -> list[Job]:
        """Retrieve all job entries."""
        return self.session.exec(select(Job).offset(offset).limit(limit)).all()

    def update(self, job_id: str, job: JobUpdate) -> Job:
        """Update an existing job entry."""
        db_job = self.read_job(job_id)
        if not db_job:
            return None
        job_data = job.model_dump(exclude_unset=True)
        db_job.sqlmodel_update(job_data)
        self.session.add(db_job)
        self.session.commit()
        self.session.refresh(db_job)
        return db_job

    def delete(self, job_id: str) -> bool:
        """Delete a job entry by ID."""
        job = self.read_job(job_id)
        if job:
            self.session.delete(job)
            self.session.commit()
            return True
        return False
