from sqlalchemy.orm import Session
from typing import Optional, List
from src.models.favorite import Favorite
from src.repositories.base_repository import BaseRepository


class FavoriteRepository(BaseRepository):
    def __init__(self, db_session: Session):
        super().__init__(db_session)
        self.model = Favorite

    def get_favorite_by_id(self, favorite_id: int) -> Optional[Favorite]:
        return self.get(self.model, favorite_id)

    def add_favorite(self, account_id: int, job_id: int) -> Favorite:
        new_favorite = self.model(account_id=account_id, job_id=job_id)
        return self.add(new_favorite)

    def get_favorites_by_account_id(self, account_id: int) -> List[Favorite]:
        return self.db_session.query(self.model).filter(self.model.account_id == account_id).all()

    def get_favorites_by_job_id(self, job_id: int) -> List[Favorite]:
        return self.db_session.query(self.model).filter(self.model.job_id == job_id).all()

    def delete_favorite(self, account_id: int, job_id: int) -> bool:
        favorite = self.db_session.query(self.model).filter(
            self.model.account_id == account_id,
            self.model.job_id == job_id
        ).first()
        if favorite:
            self.delete(favorite)
            return True
        return False

    def favorite_exists(self, account_id: int, job_id: int) -> bool:
        return self.db_session.query(self.model).filter(
            self.model.account_id == account_id,
            self.model.job_id == job_id
        ).count() > 0
