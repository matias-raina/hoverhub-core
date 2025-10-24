from sqlalchemy.orm import Session
from typing import Optional, List
from src.models.job_poster_profile import JobPosterProfile
from src.repositories.base_repository import BaseRepository


class JobPosterProfileRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = JobPosterProfile

    def get_profile_by_id(self, profile_id: int) -> Optional[JobPosterProfile]:
        return self.get(self.model, profile_id)

    def get_profile_by_account_id(self, account_id: int) -> Optional[JobPosterProfile]:
        return self.db_session.query(self.model).filter(self.model.account_id == account_id).first()

    def create_profile(self, profile_data: dict) -> JobPosterProfile:
        profile = JobPosterProfile(**profile_data)
        return self.add(profile)

    def update_profile(self, profile_id: int, profile_data: dict) -> Optional[JobPosterProfile]:
        profile = self.get(self.model, profile_id)
        if profile:
            for key, value in profile_data.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            self.db_session.commit()
            return profile
        return None

    def delete_profile(self, profile_id: int) -> bool:
        profile = self.get(self.model, profile_id)
        if profile:
            self.delete(profile)
            return True
        return False

    def get_all_profiles(self) -> List[JobPosterProfile]:
        return self.get_all(self.model)
