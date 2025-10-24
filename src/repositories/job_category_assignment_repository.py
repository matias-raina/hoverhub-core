from sqlalchemy.orm import Session
from typing import Optional, List
from src.models.job_category_assignment import JobCategoryAssignment
from src.repositories.base_repository import BaseRepository


class JobCategoryAssignmentRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = JobCategoryAssignment

    def get_assignments_by_job_id(self, job_id: int) -> List[JobCategoryAssignment]:
        return self.db_session.query(self.model).filter(self.model.job_id == job_id).all()

    def get_assignments_by_category_id(self, job_category_id: int) -> List[JobCategoryAssignment]:
        return self.db_session.query(self.model).filter(
            self.model.job_category_id == job_category_id
        ).all()

    def create_assignment(self, job_id: int, job_category_id: int) -> JobCategoryAssignment:
        assignment = JobCategoryAssignment(job_id=job_id, job_category_id=job_category_id)
        return self.add(assignment)

    def delete_assignment(self, job_id: int, job_category_id: int) -> bool:
        assignment = self.db_session.query(self.model).filter(
            self.model.job_id == job_id,
            self.model.job_category_id == job_category_id
        ).first()
        if assignment:
            self.delete(assignment)
            return True
        return False

    def delete_assignments_by_job_id(self, job_id: int) -> bool:
        assignments = self.get_assignments_by_job_id(job_id)
        for assignment in assignments:
            self.delete(assignment)
        return True

    def assignment_exists(self, job_id: int, job_category_id: int) -> bool:
        return self.db_session.query(self.model).filter(
            self.model.job_id == job_id,
            self.model.job_category_id == job_category_id
        ).count() > 0
