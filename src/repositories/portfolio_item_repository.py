from sqlalchemy.orm import Session
from typing import Optional, List
from src.models.portfolio_item import PortfolioItem
from src.repositories.base_repository import BaseRepository


class PortfolioItemRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = PortfolioItem

    def get_item_by_id(self, item_id: int) -> Optional[PortfolioItem]:
        return self.get(self.model, item_id)

    def get_items_by_droner_profile_id(self, droner_profile_id: int) -> List[PortfolioItem]:
        return self.db_session.query(self.model).filter(
            self.model.droner_profile_id == droner_profile_id
        ).order_by(self.model.created_at.desc()).all()

    def create_item(self, item_data: dict) -> PortfolioItem:
        item = PortfolioItem(**item_data)
        return self.add(item)

    def update_item(self, item_id: int, item_data: dict) -> Optional[PortfolioItem]:
        item = self.get(self.model, item_id)
        if item:
            for key, value in item_data.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            self.db_session.commit()
            return item
        return None

    def delete_item(self, item_id: int) -> bool:
        item = self.get(self.model, item_id)
        if item:
            self.delete(item)
            return True
        return False
