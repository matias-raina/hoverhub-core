from typing import Optional
from uuid import UUID

from sqlmodel import Session, select

from app.domain.models.user import User
from app.domain.repositories.interfaces.user import IUserRepository


class UserRepository(IUserRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(self, user: User) -> User:
        """Create a new user in the database."""
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by email."""
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieve a user by ID."""
        return self.session.get(User, user_id)

    def update(self, user: User) -> User:
        """Update an existing user."""
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete(self, user_id: UUID) -> bool:
        """Delete a user by ID."""
        user = self.get_by_id(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
        return False
