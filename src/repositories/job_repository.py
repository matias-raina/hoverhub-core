from sqlalchemy.orm import Session
from typing import Optional, List
from src.models.job import Job
from src.repositories.base_repository import BaseRepository


class JobRepository(BaseRepository):
    def __init__(self, db_session: Session):
        super().__init__(db_session)
        self.model = Job

    def get_job_by_id(self, job_id: int) -> Optional[Job]:
        return self.get(self.model, job_id)

    def get_jobs_by_account_id(self, account_id: int) -> List[Job]:
        return self.db_session.query(self.model).filter(self.model.account_id == account_id).all()

    def create_job(self, job_data: dict) -> Job:
        new_job = Job(**job_data)
        return self.add(new_job)

    def update_job(self, job_id: int, job_data: dict) -> Optional[Job]:
        job = self.get_job_by_id(job_id)
        if job:
            for key, value in job_data.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            self.db_session.commit()
            return job
        return None

    def delete_job(self, job_id: int) -> bool:
        job = self.get_job_by_id(job_id)
        if job:
            self.delete(job)
            return True
        return False

    def get_all_jobs(self) -> List[Job]:
        return self.get_all(self.model)

    def search_jobs(self, filters: dict) -> List[Job]:
        query = self.db_session.query(self.model)

        if filters.get('location'):
            query = query.filter(self.model.location.ilike(
                f"%{filters['location']}%"))

        if filters.get('min_budget'):
            query = query.filter(self.model.budget >= filters['min_budget'])

        if filters.get('max_budget'):
            query = query.filter(self.model.budget <= filters['max_budget'])

        return query.all()
