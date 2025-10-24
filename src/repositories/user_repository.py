from sqlalchemy.orm import Session
from typing import Optional
from src.models.user import User
from src.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = User

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.get(self.model, user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db_session.query(self.model).filter(self.model.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db_session.query(self.model).filter(self.model.email == email).first()

    def create_user(self, user_data: dict) -> User:
        user = User(**user_data)
        return self.add(user)

    def update_user(self, user_id: int, user_data: dict) -> Optional[User]:
        user = self.get(self.model, user_id)
        if user:
            for key, value in user_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            self.db_session.commit()
            return user
        return None

    def delete_user(self, user_id: int) -> bool:
        user = self.get(self.model, user_id)
        if user:
            self.delete(user)
            return True
        return False

    def get_all_users(self):
        return self.get_all(self.model)