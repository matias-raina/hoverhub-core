from uuid import uuid4

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

    def test_delete_application_success(self, db_session):
        """Test deleting an application successfully"""
        # Arrange
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)
        job = create_test_job(db_session, account.id)
        application = create_test_application(db_session, job.id, account.id)

        repository = ApplicationRepository(db_session)

        # Act
        result = repository.delete(application.id)

        # Assert
        assert result is True
        # Verify application was deleted
        deleted_app = repository.get_by_id(application.id)
        assert deleted_app is None

    def test_delete_application_not_found(self, db_session):
        """Test deleting an application that doesn't exist"""
        # Arrange
        repository = ApplicationRepository(db_session)
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
