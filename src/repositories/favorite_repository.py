class FavoriteRepository(BaseRepository):
    def __init__(self, db_session):
        super().__init__(db_session)
        self.model = Favorite

    def add_favorite(self, user_id: int, job_id: int) -> Favorite:
        new_favorite = self.model(user_id=user_id, job_id=job_id)
        self.add(new_favorite)
        return new_favorite

    def get_favorites(self, user_id: int) -> List[Favorite]:
        return self.db_session.query(self.model).filter(self.model.user_id == user_id).all()

    def delete_favorite(self, user_id: int, job_id: int) -> bool:
        favorite = self.db_session.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.job_id == job_id
        ).first()
        if favorite:
            self.delete(favorite)
            return True
        return False

    def favorite_exists(self, user_id: int, job_id: int) -> bool:
        return self.db_session.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.job_id == job_id
        ).count() > 0
