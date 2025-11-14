from collections.abc import Sequence
from uuid import UUID

from sqlmodel import Session, desc, select

from app.domain.models.job import Job, JobUpdate
from app.domain.repositories.interfaces.job import IJobRepository


class JobRepository(IJobRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(self, job: Job) -> Job:
        """Create a new job entry in the database."""
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job

    def get_by_id(self, job_id: UUID) -> Job | None:
        """Retrieve a job entry by ID."""
        return self.session.get(Job, job_id)

    def get_all(self, offset: int = 0, limit: int = 100) -> Sequence[Job]:
        """Retrieve all job entries ordered by creation date (newest first)."""
        return list(
            self.session.exec(
                select(Job).order_by(desc(Job.created_at)).offset(offset).limit(limit)
            ).all()
        )

    def update(self, job_id: UUID, job: JobUpdate) -> Job | None:
        """Update an existing job entry."""
        db_job = self.get_by_id(job_id)
        if not db_job:
            return None
        job_data = job.model_dump(exclude_unset=True)
        db_job.sqlmodel_update(job_data)
        self.session.add(db_job)
        self.session.commit()
        self.session.refresh(db_job)
        return db_job

    def delete(self, job_id: UUID) -> bool:
        """Delete a job entry by ID."""
        job = self.get_by_id(job_id)
        if job:
            self.session.delete(job)
            self.session.commit()
            return True
        return False

    def get_total_applications(self, job_id: UUID) -> int:
        """Get the total number of applications for a job."""
        job = self.get_by_id(job_id)
        if not job:
            return 0
        return len(job.applications)
