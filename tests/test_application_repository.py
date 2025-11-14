from uuid import uuid4

from app.domain.models.account import AccountType
from app.domain.models.application import ApplicationStatus, ApplicationUpdate
from app.domain.repositories.application import ApplicationRepository
from tests.utils import (
    create_test_account,
    create_test_application,
    create_test_job,
    create_test_user,
)


class TestApplicationRepositoryDelete:
    """Tests for ApplicationRepository.delete"""

    def test_delete_existing_application_returns_true(self, db_session):
        """Test deleting an existing application returns True"""
        # Arrange
        user = create_test_user(db_session)
        employer_account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )
        droner_account = create_test_account(
            db_session, user.id, name="Droner Account", account_type=AccountType.DRONER
        )
        job = create_test_job(db_session, employer_account.id)
        application = create_test_application(db_session, job.id, droner_account.id)

        repository = ApplicationRepository(db_session)

        # Act
        result = repository.delete(application.id)

        # Assert
        assert result is True

    def test_delete_removes_application_from_database(self, db_session):
        """Test that delete actually removes the application from the database"""
        # Arrange
        user = create_test_user(db_session)
        employer_account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )
        droner_account = create_test_account(
            db_session, user.id, name="Droner Account", account_type=AccountType.DRONER
        )
        job = create_test_job(db_session, employer_account.id)
        application = create_test_application(db_session, job.id, droner_account.id)
        application_id = application.id

        repository = ApplicationRepository(db_session)

        # Act
        repository.delete(application_id)

        # Assert - application should not exist anymore
        deleted_application = repository.get_by_id(application_id)
        assert deleted_application is None

    def test_delete_non_existent_application_returns_false(self, db_session):
        """Test deleting a non-existent application returns False"""
        # Arrange
        repository = ApplicationRepository(db_session)
        fake_application_id = uuid4()

        # Act
        result = repository.delete(fake_application_id)

        # Assert
        assert result is False

    def test_delete_already_deleted_application_returns_false(self, db_session):
        """Test deleting an already deleted application returns False"""
        # Arrange
        user = create_test_user(db_session)
        employer_account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )
        droner_account = create_test_account(
            db_session, user.id, name="Droner Account", account_type=AccountType.DRONER
        )
        job = create_test_job(db_session, employer_account.id)
        application = create_test_application(db_session, job.id, droner_account.id)
        application_id = application.id

        repository = ApplicationRepository(db_session)

        # Act - delete first time
        first_result = repository.delete(application_id)
        # Act - delete second time
        second_result = repository.delete(application_id)

        # Assert
        assert first_result is True
        assert second_result is False

    def test_delete_does_not_affect_other_applications(self, db_session):
        """Test that deleting one application doesn't affect other applications"""
        # Arrange
        user = create_test_user(db_session)
        employer_account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )
        droner_account1 = create_test_account(
            db_session, user.id, name="Droner Account 1", account_type=AccountType.DRONER
        )
        droner_account2 = create_test_account(
            db_session, user.id, name="Droner Account 2", account_type=AccountType.DRONER
        )
        job = create_test_job(db_session, employer_account.id)
        application1 = create_test_application(db_session, job.id, droner_account1.id)
        application2 = create_test_application(db_session, job.id, droner_account2.id)

        repository = ApplicationRepository(db_session)

        # Act - delete only application1
        repository.delete(application1.id)

        # Assert - application2 should still exist
        remaining_application = repository.get_by_id(application2.id)
        assert remaining_application is not None
        assert remaining_application.id == application2.id

    def test_delete_does_not_delete_related_job(self, db_session):
        """Test that deleting an application doesn't delete the related job"""
        # Arrange
        user = create_test_user(db_session)
        employer_account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )
        droner_account = create_test_account(
            db_session, user.id, name="Droner Account", account_type=AccountType.DRONER
        )
        job = create_test_job(db_session, employer_account.id)
        application = create_test_application(db_session, job.id, droner_account.id)

        repository = ApplicationRepository(db_session)

        # Act
        repository.delete(application.id)

        # Assert - job should still exist
        # We need to import JobRepository to check this
        from app.domain.repositories.job import JobRepository

        job_repository = JobRepository(db_session)
        remaining_job = job_repository.get_by_id(job.id)
        assert remaining_job is not None
        assert remaining_job.id == job.id

    def test_delete_does_not_delete_related_account(self, db_session):
        """Test that deleting an application doesn't delete the related account"""
        # Arrange
        user = create_test_user(db_session)
        employer_account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )
        droner_account = create_test_account(
            db_session, user.id, name="Droner Account", account_type=AccountType.DRONER
        )
        job = create_test_job(db_session, employer_account.id)
        application = create_test_application(db_session, job.id, droner_account.id)

        repository = ApplicationRepository(db_session)

        # Act
        repository.delete(application.id)

        # Assert - account should still exist
        from app.domain.repositories.account import AccountRepository

        account_repository = AccountRepository(db_session)
        remaining_account = account_repository.get_by_id(droner_account.id)
        assert remaining_account is not None
        assert remaining_account.id == droner_account.id

    def test_delete_multiple_applications_sequentially(self, db_session):
        """Test deleting multiple applications one by one"""
        # Arrange
        user = create_test_user(db_session)
        employer_account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )
        droner_account1 = create_test_account(
            db_session, user.id, name="Droner Account 1", account_type=AccountType.DRONER
        )
        droner_account2 = create_test_account(
            db_session, user.id, name="Droner Account 2", account_type=AccountType.DRONER
        )
        droner_account3 = create_test_account(
            db_session, user.id, name="Droner Account 3", account_type=AccountType.DRONER
        )
        job = create_test_job(db_session, employer_account.id)
        application1 = create_test_application(db_session, job.id, droner_account1.id)
        application2 = create_test_application(db_session, job.id, droner_account2.id)
        application3 = create_test_application(db_session, job.id, droner_account3.id)

        repository = ApplicationRepository(db_session)

        # Act - delete all three applications
        result1 = repository.delete(application1.id)
        result2 = repository.delete(application2.id)
        result3 = repository.delete(application3.id)

        # Assert
        assert result1 is True
        assert result2 is True
        assert result3 is True

        # Verify all are deleted
        assert repository.get_by_id(application1.id) is None
        assert repository.get_by_id(application2.id) is None
        assert repository.get_by_id(application3.id) is None

    def test_delete_application_with_different_statuses(self, db_session):
        """Test that delete works regardless of application status"""
        # Arrange
        user = create_test_user(db_session)
        employer_account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )
        droner_account = create_test_account(
            db_session, user.id, name="Droner Account", account_type=AccountType.DRONER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create applications with different statuses
        pending_app = create_test_application(
            db_session, job.id, droner_account.id, status=ApplicationStatus.PENDING
        )
        accepted_app = create_test_application(
            db_session,
            job.id,
            create_test_account(
                db_session, user.id, name="Droner 2", account_type=AccountType.DRONER
            ).id,
            status=ApplicationStatus.ACCEPTED,
        )
        rejected_app = create_test_application(
            db_session,
            job.id,
            create_test_account(
                db_session, user.id, name="Droner 3", account_type=AccountType.DRONER
            ).id,
            status=ApplicationStatus.REJECTED,
        )

        repository = ApplicationRepository(db_session)

        # Act - delete applications with different statuses
        result1 = repository.delete(pending_app.id)
        result2 = repository.delete(accepted_app.id)
        result3 = repository.delete(rejected_app.id)

        # Assert
        assert result1 is True
        assert result2 is True
        assert result3 is True

        # Verify all are deleted
        assert repository.get_by_id(pending_app.id) is None
        assert repository.get_by_id(accepted_app.id) is None
        assert repository.get_by_id(rejected_app.id) is None

    def test_delete_with_invalid_uuid_format(self, db_session):
        """Test delete with properly formatted UUID that doesn't exist"""
        # Arrange
        repository = ApplicationRepository(db_session)
        # Create a valid UUID that doesn't correspond to any application
        non_existent_id = uuid4()

        # Act
        result = repository.delete(non_existent_id)

        # Assert
        assert result is False


class TestApplicationRepositoryUpdate:
    """Tests for ApplicationRepository.update"""

    def test_update_application_success(self, db_session):
        """Test updating an application successfully"""
        # Arrange
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)
        job = create_test_job(db_session, account.id)
        application = create_test_application(
            db_session, job.id, account.id, message="Original message"
        )

        repository = ApplicationRepository(db_session)
        update_data = ApplicationUpdate(
            message="Updated message", status=ApplicationStatus.ACCEPTED
        )

        # Act
        result = repository.update(application.id, update_data)

        # Assert
        assert result is not None
        assert result.id == application.id
        assert result.message == "Updated message"
        assert result.status == ApplicationStatus.ACCEPTED

    def test_update_application_not_found(self, db_session):
        """Test updating an application that doesn't exist"""
        # Arrange
        repository = ApplicationRepository(db_session)
        non_existent_id = uuid4()
        update_data = ApplicationUpdate(message="Updated message")

        # Act
        result = repository.update(non_existent_id, update_data)

        # Assert
        assert result is None
