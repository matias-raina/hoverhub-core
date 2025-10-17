from sqlalchemy.orm import Session
from src.models.user import User
from src.repositories.base_repository import BaseRepository
from src.schemas.user import UserCreate, UserResponse

class UserRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = User

    def get_user_by_id(self, user_id: int) -> UserResponse:
        return self.get(user_id)

    def create_user(self, user_data: UserCreate) -> UserResponse:
        user = User(**user_data.dict())
        self.add(user)
        return user

    def update_user(self, user_id: int, user_data: UserCreate) -> UserResponse:
        user = self.get(user_id)
        for key, value in user_data.dict().items():
            setattr(user, key, value)
        self.db.commit()
        return user

    def delete_user(self, user_id: int) -> None:
        user = self.get(user_id)
        self.delete(user)