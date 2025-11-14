from uuid import uuid4

from app.domain.models.account import AccountType
from app.domain.models.application import ApplicationStatus
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

    def test_get_total_applications_no_applications(self, db_session):
        """Test getting total applications when a job has no applications"""
        # Arrange
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id, account_type=AccountType.EMPLOYER)
        job = create_test_job(db_session, account.id)

        repository = JobRepository(db_session)

        # Act
        total = repository.get_total_applications(job.id)

        # Assert
        assert total == 0

    def test_get_total_applications_single_application(self, db_session):
        """Test getting total applications when a job has one application"""
        # Arrange
        user = create_test_user(db_session)
        employer_account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )
        droner_account = create_test_account(
            db_session, user.id, name="Droner Account", account_type=AccountType.DRONER
        )
        job = create_test_job(db_session, employer_account.id)
        create_test_application(db_session, job.id, droner_account.id)

        repository = JobRepository(db_session)

        # Act
        total = repository.get_total_applications(job.id)

        # Assert
        assert total == 1

    def test_get_total_applications_multiple_applications(self, db_session):
        """Test getting total applications when a job has multiple applications"""
        # Arrange
        user = create_test_user(db_session)
        employer_account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )
        droner_account1 = create_test_account(
            db_session, user.id, name="Droner 1", account_type=AccountType.DRONER
        )
        droner_account2 = create_test_account(
            db_session, user.id, name="Droner 2", account_type=AccountType.DRONER
        )
        droner_account3 = create_test_account(
            db_session, user.id, name="Droner 3", account_type=AccountType.DRONER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create 3 applications
        create_test_application(db_session, job.id, droner_account1.id)
        create_test_application(db_session, job.id, droner_account2.id)
        create_test_application(db_session, job.id, droner_account3.id)

        repository = JobRepository(db_session)

        # Act
        total = repository.get_total_applications(job.id)

        # Assert
        assert total == 3

    def test_get_total_applications_non_existent_job(self, db_session):
        """Test getting total applications for a non-existent job returns 0"""
        # Arrange
        repository = JobRepository(db_session)
        fake_job_id = uuid4()

        # Act
        total = repository.get_total_applications(fake_job_id)

        # Assert
        assert total == 0

    def test_get_total_applications_includes_all_statuses(self, db_session):
        """Test that get_total_applications counts applications with all statuses"""
        # Arrange
        user = create_test_user(db_session)
        employer_account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )
        droner_account1 = create_test_account(
            db_session, user.id, name="Droner 1", account_type=AccountType.DRONER
        )
        droner_account2 = create_test_account(
            db_session, user.id, name="Droner 2", account_type=AccountType.DRONER
        )
        droner_account3 = create_test_account(
            db_session, user.id, name="Droner 3", account_type=AccountType.DRONER
        )
        droner_account4 = create_test_account(
            db_session, user.id, name="Droner 4", account_type=AccountType.DRONER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create applications with different statuses
        create_test_application(
            db_session, job.id, droner_account1.id, status=ApplicationStatus.PENDING
        )
        create_test_application(
            db_session, job.id, droner_account2.id, status=ApplicationStatus.ACCEPTED
        )
        create_test_application(
            db_session, job.id, droner_account3.id, status=ApplicationStatus.REJECTED
        )
        create_test_application(
            db_session, job.id, droner_account4.id, status=ApplicationStatus.WITHDRAWN
        )

        repository = JobRepository(db_session)

        # Act
        total = repository.get_total_applications(job.id)

        # Assert - should count all 4 applications regardless of status
        assert total == 4

    def test_get_total_applications_multiple_jobs(self, db_session):
        """Test that get_total_applications only counts applications for the specific job"""
        # Arrange
        user = create_test_user(db_session)
        employer_account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )
        droner_account1 = create_test_account(
            db_session, user.id, name="Droner 1", account_type=AccountType.DRONER
        )
        droner_account2 = create_test_account(
            db_session, user.id, name="Droner 2", account_type=AccountType.DRONER
        )
        droner_account3 = create_test_account(
            db_session, user.id, name="Droner 3", account_type=AccountType.DRONER
        )

        job1 = create_test_job(db_session, employer_account.id, title="Job 1")
        job2 = create_test_job(db_session, employer_account.id, title="Job 2")

        # Create 2 applications for job1 and 3 applications for job2
        create_test_application(db_session, job1.id, droner_account1.id)
        create_test_application(db_session, job1.id, droner_account2.id)

        create_test_application(db_session, job2.id, droner_account1.id)
        create_test_application(db_session, job2.id, droner_account2.id)
        create_test_application(db_session, job2.id, droner_account3.id)

        repository = JobRepository(db_session)

        # Act
        total_job1 = repository.get_total_applications(job1.id)
        total_job2 = repository.get_total_applications(job2.id)

        # Assert - each job should have its own count
        assert total_job1 == 2
        assert total_job2 == 3

    def test_get_total_applications_after_deletion(self, db_session):
        """Test that get_total_applications updates correctly after an application is deleted"""
        # Arrange
        user = create_test_user(db_session)
        employer_account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )
        droner_account1 = create_test_account(
            db_session, user.id, name="Droner 1", account_type=AccountType.DRONER
        )
        droner_account2 = create_test_account(
            db_session, user.id, name="Droner 2", account_type=AccountType.DRONER
        )
        job = create_test_job(db_session, employer_account.id)

        application1 = create_test_application(db_session, job.id, droner_account1.id)
        application2 = create_test_application(db_session, job.id, droner_account2.id)

        repository = JobRepository(db_session)

        # Verify initial count
        initial_total = repository.get_total_applications(job.id)
        assert initial_total == 2

        # Delete one application
        from app.domain.repositories.application import ApplicationRepository

        app_repository = ApplicationRepository(db_session)
        app_repository.delete(application1.id)

        # Act - get total after deletion
        total_after_delete = repository.get_total_applications(job.id)

        # Assert - count should decrease
        assert total_after_delete == 1

    def test_get_total_applications_returns_integer(self, db_session):
        """Test that get_total_applications returns an integer"""
        # Arrange
        user = create_test_user(db_session)
        employer_account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )
        droner_account = create_test_account(
            db_session, user.id, name="Droner Account", account_type=AccountType.DRONER
        )
        job = create_test_job(db_session, employer_account.id)
        create_test_application(db_session, job.id, droner_account.id)

        repository = JobRepository(db_session)

        # Act
        total = repository.get_total_applications(job.id)

        # Assert
        assert isinstance(total, int)

    def test_get_total_applications_large_number(self, db_session):
        """Test getting total applications with a large number of applications"""
        # Arrange
        user = create_test_user(db_session)
        employer_account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create 10 applications
        for i in range(10):
            droner_account = create_test_account(
                db_session,
                user.id,
                name=f"Droner {i}",
                account_type=AccountType.DRONER,
            )
            create_test_application(db_session, job.id, droner_account.id)

        repository = JobRepository(db_session)

        # Act
        total = repository.get_total_applications(job.id)

        # Assert
        assert total == 10

    def test_get_total_applications_with_messages(self, db_session):
        """Test that get_total_applications counts applications regardless of message content"""
        # Arrange
        user = create_test_user(db_session)
        employer_account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )
        droner_account1 = create_test_account(
            db_session, user.id, name="Droner 1", account_type=AccountType.DRONER
        )
        droner_account2 = create_test_account(
            db_session, user.id, name="Droner 2", account_type=AccountType.DRONER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create applications with and without messages
        create_test_application(db_session, job.id, droner_account1.id, message="I'm interested!")
        create_test_application(db_session, job.id, droner_account2.id, message=None)

        repository = JobRepository(db_session)

        # Act
        total = repository.get_total_applications(job.id)

        # Assert - should count both applications
        assert total == 2

    def test_get_total_applications_consistency(self, db_session):
        """Test that get_total_applications returns consistent results"""
        # Arrange
        user = create_test_user(db_session)
        employer_account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )
        droner_account = create_test_account(
            db_session, user.id, name="Droner Account", account_type=AccountType.DRONER
        )
        job = create_test_job(db_session, employer_account.id)
        create_test_application(db_session, job.id, droner_account.id)

        repository = JobRepository(db_session)

        # Act - call multiple times
        total1 = repository.get_total_applications(job.id)
        total2 = repository.get_total_applications(job.id)
        total3 = repository.get_total_applications(job.id)

        # Assert - should return the same result each time
        assert total1 == total2 == total3 == 1
