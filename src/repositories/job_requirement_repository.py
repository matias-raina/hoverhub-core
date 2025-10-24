from sqlalchemy.orm import Session
from typing import Optional, List
from src.models.job_requirement import JobRequirement
from src.repositories.base_repository import BaseRepository


class JobRequirementRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = JobRequirement

    def get_requirement_by_id(self, requirement_id: int) -> Optional[JobRequirement]:
        return self.get(self.model, requirement_id)

    def get_requirements_by_job_id(self, job_id: int) -> List[JobRequirement]:
        return self.db_session.query(self.model).filter(self.model.job_id == job_id).all()

    def create_requirement(self, requirement_data: dict) -> JobRequirement:
        requirement = JobRequirement(**requirement_data)
        return self.add(requirement)

    def update_requirement(self, requirement_id: int, requirement_data: dict) -> Optional[JobRequirement]:
        requirement = self.get(self.model, requirement_id)
        if requirement:
            for key, value in requirement_data.items():
                if hasattr(requirement, key):
                    setattr(requirement, key, value)
            self.db_session.commit()
            return requirement
        return None

    def delete_requirement(self, requirement_id: int) -> bool:
        requirement = self.get(self.model, requirement_id)
        if requirement:
            self.delete(requirement)
            return True
        return False

    def delete_requirements_by_job_id(self, job_id: int) -> bool:
        requirements = self.get_requirements_by_job_id(job_id)
        for requirement in requirements:
            self.delete(requirement)
        return True
