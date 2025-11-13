from collections.abc import Sequence
from uuid import UUID

from sqlmodel import Session, select

from app.domain.models.favorite import Favorite
from app.domain.repositories.interfaces.favorite import IFavoriteRepository


class FavoriteRepository(IFavoriteRepository):
    """Favorite repository."""

    def __init__(self, session: Session):
        """Initialize the favorite repository."""
        self.session = session

    def create(self, favorite: Favorite) -> Favorite:
        """Create a new favorite entry in the database."""
        self.session.add(favorite)
        self.session.commit()
        self.session.refresh(favorite)
        return favorite

    def get_by_id(self, favorite_id: UUID) -> Favorite | None:
        """Retrieve a favorite entry by ID."""
        return self.session.get(Favorite, favorite_id)

    def get_by_account_id(self, account_id: UUID) -> Sequence[Favorite]:
        """Retrieve favorite entries by Account ID."""
        statement = select(Favorite).where(Favorite.account_id == account_id)
        return self.session.exec(statement).all()

    def get_all(self, offset: int = 0, limit: int = 100) -> Sequence[Favorite]:
        """Retrieve all favorite entries."""
        return self.session.exec(select(Favorite).offset(offset).limit(limit)).all()

    def delete(self, favorite_id: UUID) -> bool:
        """Delete a favorite entry by ID."""
        favorite = self.get_by_id(favorite_id)
        if favorite:
            self.session.delete(favorite)
            self.session.commit()
            return True
        return False
