from uuid import uuid4

from app.domain.repositories.favorite import FavoriteRepository
from tests.utils import (
    create_test_account,
    create_test_favorite,
    create_test_job,
    create_test_user,
)


class TestFavoriteRepositoryGetAll:
    """Tests for FavoriteRepository.get_all"""

    def test_get_all_no_favorites(self, db_session):
        """Test getting all favorites when there are none"""
        # Arrange
        repository = FavoriteRepository(db_session)

        # Act
        favorites = repository.get_all()

        # Assert
        assert len(favorites) == 0
        assert isinstance(favorites, list) or hasattr(favorites, "__iter__")

    def test_get_all_single_favorite(self, db_session):
        """Test getting all favorites when there is one favorite"""
        # Arrange
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)
        job = create_test_job(db_session, account.id)
        favorite = create_test_favorite(db_session, account.id, job.id)

        repository = FavoriteRepository(db_session)

        # Act
        favorites = repository.get_all()

        # Assert
        assert len(favorites) == 1
        assert favorites[0].id == favorite.id
        assert favorites[0].account_id == account.id
        assert favorites[0].job_id == job.id

    def test_get_all_multiple_favorites(self, db_session):
        """Test getting all favorites when there are multiple favorites"""
        # Arrange
        user1 = create_test_user(db_session, email="user1@test.com")
        user2 = create_test_user(db_session, email="user2@test.com")
        account1 = create_test_account(db_session, user1.id)
        account2 = create_test_account(db_session, user2.id)

        job1 = create_test_job(db_session, account1.id)
        job2 = create_test_job(db_session, account1.id)
        job3 = create_test_job(db_session, account2.id)

        favorite1 = create_test_favorite(db_session, account1.id, job1.id)
        favorite2 = create_test_favorite(db_session, account1.id, job2.id)
        favorite3 = create_test_favorite(db_session, account2.id, job3.id)

        repository = FavoriteRepository(db_session)

        # Act
        favorites = repository.get_all()

        # Assert
        assert len(favorites) == 3
        favorite_ids = {fav.id for fav in favorites}
        assert favorite1.id in favorite_ids
        assert favorite2.id in favorite_ids
        assert favorite3.id in favorite_ids

    def test_get_all_with_default_parameters(self, db_session):
        """Test getting all favorites with default offset and limit"""
        # Arrange
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Create 5 favorites
        favorites_created = []
        for i in range(5):
            job = create_test_job(db_session, account.id, title=f"Job {i}")
            fav = create_test_favorite(db_session, account.id, job.id)
            favorites_created.append(fav)

        repository = FavoriteRepository(db_session)

        # Act - using default parameters (offset=0, limit=100)
        favorites = repository.get_all()

        # Assert
        assert len(favorites) == 5
        favorite_ids = {fav.id for fav in favorites}
        assert all(fav.id in favorite_ids for fav in favorites_created)

    def test_get_all_with_limit(self, db_session):
        """Test getting all favorites with a limit parameter"""
        # Arrange
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Create 5 favorites
        favorites_created = []
        for i in range(5):
            job = create_test_job(db_session, account.id, title=f"Job {i}")
            fav = create_test_favorite(db_session, account.id, job.id)
            favorites_created.append(fav)

        repository = FavoriteRepository(db_session)

        # Act - limit to 3
        favorites = repository.get_all(limit=3)

        # Assert
        assert len(favorites) == 3

    def test_get_all_with_offset(self, db_session):
        """Test getting all favorites with an offset parameter"""
        # Arrange
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Create 5 favorites
        favorites_created = []
        for i in range(5):
            job = create_test_job(db_session, account.id, title=f"Job {i}")
            fav = create_test_favorite(db_session, account.id, job.id)
            favorites_created.append(fav)

        repository = FavoriteRepository(db_session)

        # Act - offset by 2
        favorites = repository.get_all(offset=2)

        # Assert
        assert len(favorites) == 3  # Should return 3 (5 total - 2 offset)

    def test_get_all_with_offset_and_limit(self, db_session):
        """Test getting all favorites with both offset and limit"""
        # Arrange
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Create 10 favorites
        favorites_created = []
        for i in range(10):
            job = create_test_job(db_session, account.id, title=f"Job {i}")
            fav = create_test_favorite(db_session, account.id, job.id)
            favorites_created.append(fav)

        repository = FavoriteRepository(db_session)

        # Act - offset by 3, limit to 4
        favorites = repository.get_all(offset=3, limit=4)

        # Assert
        assert len(favorites) == 4

    def test_get_all_limit_larger_than_total(self, db_session):
        """Test getting all favorites when limit is larger than total count"""
        # Arrange
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Create 3 favorites
        for i in range(3):
            job = create_test_job(db_session, account.id, title=f"Job {i}")
            create_test_favorite(db_session, account.id, job.id)

        repository = FavoriteRepository(db_session)

        # Act - limit to 10 (more than total)
        favorites = repository.get_all(limit=10)

        # Assert
        assert len(favorites) == 3  # Should return all 3, not 10

    def test_get_all_offset_beyond_total(self, db_session):
        """Test getting all favorites when offset is beyond total count"""
        # Arrange
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Create 3 favorites
        for i in range(3):
            job = create_test_job(db_session, account.id, title=f"Job {i}")
            create_test_favorite(db_session, account.id, job.id)

        repository = FavoriteRepository(db_session)

        # Act - offset by 5 (more than total)
        favorites = repository.get_all(offset=5)

        # Assert
        assert len(favorites) == 0  # Should return empty list

    def test_get_all_offset_zero_limit_zero(self, db_session):
        """Test getting all favorites with offset=0 and limit=0"""
        # Arrange
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Create 3 favorites
        for i in range(3):
            job = create_test_job(db_session, account.id, title=f"Job {i}")
            create_test_favorite(db_session, account.id, job.id)

        repository = FavoriteRepository(db_session)

        # Act - limit to 0
        favorites = repository.get_all(offset=0, limit=0)

        # Assert
        assert len(favorites) == 0

    def test_get_all_returns_sequence(self, db_session):
        """Test that get_all returns a Sequence type"""
        # Arrange
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)
        job = create_test_job(db_session, account.id)
        create_test_favorite(db_session, account.id, job.id)

        repository = FavoriteRepository(db_session)

        # Act
        favorites = repository.get_all()

        # Assert
        assert hasattr(favorites, "__iter__")
        assert hasattr(favorites, "__len__")
        # Should be able to convert to list
        favorites_list = list(favorites)
        assert isinstance(favorites_list, list)

    def test_get_all_multiple_accounts_multiple_jobs(self, db_session):
        """Test getting all favorites across multiple accounts and jobs"""
        # Arrange
        user1 = create_test_user(db_session, email="user1@test.com")
        user2 = create_test_user(db_session, email="user2@test.com")
        account1 = create_test_account(db_session, user1.id)
        account2 = create_test_account(db_session, user2.id)

        # Create multiple jobs for account1
        job1 = create_test_job(db_session, account1.id, title="Job 1")
        job2 = create_test_job(db_session, account1.id, title="Job 2")
        job3 = create_test_job(db_session, account2.id, title="Job 3")

        # Create favorites
        favorite1 = create_test_favorite(db_session, account1.id, job1.id)
        favorite2 = create_test_favorite(db_session, account1.id, job2.id)
        favorite3 = create_test_favorite(db_session, account2.id, job3.id)

        repository = FavoriteRepository(db_session)

        # Act
        favorites = repository.get_all()

        # Assert
        assert len(favorites) == 3
        favorite_ids = {fav.id for fav in favorites}
        assert favorite1.id in favorite_ids
        assert favorite2.id in favorite_ids
        assert favorite3.id in favorite_ids

        # Verify account and job relationships
        account_ids = {fav.account_id for fav in favorites}
        assert account1.id in account_ids
        assert account2.id in account_ids

        job_ids = {fav.job_id for fav in favorites}
        assert job1.id in job_ids
        assert job2.id in job_ids
        assert job3.id in job_ids


class TestFavoriteRepositoryDelete:
    """Tests for FavoriteRepository.delete"""

    def test_delete_favorite_success(self, db_session):
        """Test deleting a favorite successfully"""
        # Arrange
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)
        job = create_test_job(db_session, account.id)
        favorite = create_test_favorite(db_session, account.id, job.id)

        repository = FavoriteRepository(db_session)

        # Act
        result = repository.delete(favorite.id)

        # Assert
        assert result is True
        # Verify favorite was deleted
        deleted_favorite = repository.get_by_id(favorite.id)
        assert deleted_favorite is None

    def test_delete_favorite_not_found(self, db_session):
        """Test deleting a favorite that doesn't exist"""
        # Arrange
        repository = FavoriteRepository(db_session)
        non_existent_id = uuid4()

        # Act
        result = repository.delete(non_existent_id)

        # Assert
        assert result is False
