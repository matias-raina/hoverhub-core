class FavoriteService:
    def __init__(self, favorite_repository):
        self.favorite_repository = favorite_repository

    def add_favorite(self, user_id: int, job_id: int):
        """Add a job to the user's favorites."""
        favorite = self.favorite_repository.get_favorite(user_id, job_id)
        if favorite:
            raise ValueError("Job is already in favorites.")
        return self.favorite_repository.add_favorite(user_id, job_id)

    def get_favorites(self, user_id: int):
        """Retrieve all favorite jobs for a user."""
        return self.favorite_repository.get_favorites_by_user(user_id)

    def remove_favorite(self, user_id: int, job_id: int):
        """Remove a job from the user's favorites."""
        favorite = self.favorite_repository.get_favorite(user_id, job_id)
        if not favorite:
            raise ValueError("Job is not in favorites.")
        return self.favorite_repository.remove_favorite(user_id, job_id)