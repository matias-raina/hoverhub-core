from sqlalchemy.orm import Session
from typing import Optional, List
from src.models.license import License
from src.repositories.base_repository import BaseRepository


class LicenseRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = License

    def get_license_by_id(self, license_id: int) -> Optional[License]:
        return self.get(self.model, license_id)

    def get_licenses_by_droner_profile_id(self, droner_profile_id: int) -> List[License]:
        return self.db_session.query(self.model).filter(
            self.model.droner_profile_id == droner_profile_id
        ).all()

    def create_license(self, license_data: dict) -> License:
        license = License(**license_data)
        return self.add(license)

    def update_license(self, license_id: int, license_data: dict) -> Optional[License]:
        license = self.get(self.model, license_id)
        if license:
            for key, value in license_data.items():
                if hasattr(license, key):
                    setattr(license, key, value)
            self.db_session.commit()
            return license
        return None

    def delete_license(self, license_id: int) -> bool:
        license = self.get(self.model, license_id)
        if license:
            self.delete(license)
            return True
        return False
