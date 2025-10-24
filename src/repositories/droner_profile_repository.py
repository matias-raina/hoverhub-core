from sqlalchemy.orm import Session
from typing import Optional, List
from src.models.droner_profile import DronerProfile
from src.repositories.base_repository import BaseRepository


class DronerProfileRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = DronerProfile

    def get_profile_by_id(self, profile_id: int) -> Optional[DronerProfile]:
        return self.get(self.model, profile_id)

    def get_profile_by_account_id(self, account_id: int) -> Optional[DronerProfile]:
        return self.db_session.query(self.model).filter(self.model.account_id == account_id).first()

    def create_profile(self, profile_data: dict) -> DronerProfile:
        profile = DronerProfile(**profile_data)
        return self.add(profile)

    def update_profile(self, profile_id: int, profile_data: dict) -> Optional[DronerProfile]:
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

    def get_all_profiles(self) -> List[DronerProfile]:
        return self.get_all(self.model)

    def search_profiles(self, filters: dict) -> List[DronerProfile]:
        query = self.db_session.query(self.model)
        
        if filters.get('min_experience'):
            query = query.filter(self.model.experience_years >= filters['min_experience'])
        
        if filters.get('display_name'):
            query = query.filter(self.model.display_name.ilike(f"%{filters['display_name']}%"))
        
        return query.all()
