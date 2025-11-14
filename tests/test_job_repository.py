from uuid import uuid4

from app.domain.models.account import AccountType
from app.domain.models.job import JobUpdate
from app.domain.repositories.job import JobRepository
from tests.utils import (
    create_test_account,
    create_test_application,
    create_test_job,
    create_test_user,
)


class TestJobRepositoryUpdate:
    """Tests for JobRepository.update"""

    def test_update_job_success(self, db_session):
        """Test updating a job successfully"""
        # Arrange
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)
        job = create_test_job(
            db_session, account.id, title="Original Title", description="Original Description"
        )

        repository = JobRepository(db_session)
        update_data = JobUpdate(title="Updated Title", description="Updated Description")

        # Act
        result = repository.update(job.id, update_data)

        # Assert
        assert result is not None
        assert result.id == job.id
        assert result.title == "Updated Title"
        assert result.description == "Updated Description"

    def test_update_job_not_found(self, db_session):
        """Test updating a job that doesn't exist"""
        # Arrange
        repository = JobRepository(db_session)
        non_existent_id = uuid4()
        update_data = JobUpdate(title="Updated Title")

        # Act
        result = repository.update(non_existent_id, update_data)

        # Assert
        assert result is None


class TestJobRepositoryGetTotalApplications:
    """Tests for JobRepository.get_total_applications"""

    def test_get_total_applications_success(self, db_session):
        """Test getting total applications for a job with applications"""
        # Arrange
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)
        job = create_test_job(db_session, account.id)

        # Create droner accounts for applications
        droner_user1 = create_test_user(db_session, email="droner1@test.com")
        droner_account1 = create_test_account(
            db_session, droner_user1.id, account_type=AccountType.DRONER
        )
        droner_user2 = create_test_user(db_session, email="droner2@test.com")
        droner_account2 = create_test_account(
            db_session, droner_user2.id, account_type=AccountType.DRONER
        )

        # Create applications
        create_test_application(db_session, job.id, droner_account1.id)
        create_test_application(db_session, job.id, droner_account2.id)

        repository = JobRepository(db_session)

        # Act
        result = repository.get_total_applications(job.id)

        # Assert
        assert result == 2

    def test_get_total_applications_no_applications(self, db_session):
        """Test getting total applications for a job with no applications"""
        # Arrange
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)
        job = create_test_job(db_session, account.id)

        repository = JobRepository(db_session)

        # Act
        result = repository.get_total_applications(job.id)

        # Assert
        assert result == 0

    def test_get_total_applications_job_not_found(self, db_session):
        """Test getting total applications for a job that doesn't exist"""
        # Arrange
        repository = JobRepository(db_session)
        non_existent_id = uuid4()

        # Act
        result = repository.get_total_applications(non_existent_id)

        # Assert
        assert result == 0
