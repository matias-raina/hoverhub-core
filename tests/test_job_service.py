from datetime import UTC, date, datetime, timedelta
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException, status

from app.domain.models.job import Job
from app.domain.repositories.interfaces.job import IJobRepository
from app.dto.job import UpdateJobDto
from app.services.job import JobService


class TestJobServiceGetById:
    """Tests for JobService.get_by_id"""

    def test_get_by_id_success(self):
        """Test getting job by ID when job exists and belongs to account"""
        # Arrange
        account_id = uuid4()
        job_id = uuid4()
        mock_job = Job(
            id=job_id,
            account_id=account_id,
            title="Test Job",
            description="Test description",
            budget=1000.0,
            location="Test Location",
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=7),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        mock_job_repository = MagicMock(spec=IJobRepository)
        mock_job_repository.get_by_id.return_value = mock_job

        service = JobService(mock_job_repository)

        # Act
        result = service.get_by_id(account_id, job_id)

        # Assert
        assert result == mock_job
        mock_job_repository.get_by_id.assert_called_once_with(job_id)

    def test_get_by_id_not_found(self):
        """Test getting job by ID when job doesn't exist"""
        # Arrange
        account_id = uuid4()
        job_id = uuid4()
        mock_job_repository = MagicMock(spec=IJobRepository)
        mock_job_repository.get_by_id.return_value = None

        service = JobService(mock_job_repository)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.get_by_id(account_id, job_id)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Job not found" in str(exc_info.value.detail)
        mock_job_repository.get_by_id.assert_called_once_with(job_id)

    def test_get_by_id_unauthorized(self):
        """Test getting job by ID when job belongs to different account"""
        # Arrange
        account_id = uuid4()
        other_account_id = uuid4()
        job_id = uuid4()
        mock_job = Job(
            id=job_id,
            account_id=other_account_id,  # Different account
            title="Test Job",
            description="Test description",
            budget=1000.0,
            location="Test Location",
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=7),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        mock_job_repository = MagicMock(spec=IJobRepository)
        mock_job_repository.get_by_id.return_value = mock_job

        service = JobService(mock_job_repository)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.get_by_id(account_id, job_id)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "not authorized" in str(exc_info.value.detail).lower()
        mock_job_repository.get_by_id.assert_called_once_with(job_id)


class TestJobServiceUpdateJob:
    """Tests for JobService.update_job"""

    def test_update_job_success(self):
        """Test updating job successfully"""
        # Arrange
        account_id = uuid4()
        job_id = uuid4()
        original_job = Job(
            id=job_id,
            account_id=account_id,
            title="Original Title",
            description="Original description",
            budget=1000.0,
            location="Original Location",
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=7),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        updated_job = Job(
            id=job_id,
            account_id=account_id,
            title="Updated Title",
            description="Updated description",
            budget=2000.0,
            location="Updated Location",
            start_date=date.today() + timedelta(days=2),
            end_date=date.today() + timedelta(days=8),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        mock_job_repository = MagicMock(spec=IJobRepository)
        mock_job_repository.get_by_id.return_value = original_job
        mock_job_repository.update.return_value = updated_job

        service = JobService(mock_job_repository)
        dto = UpdateJobDto(title="Updated Title", description="Updated description", budget=2000.0)

        # Act
        result = service.update_job(account_id, job_id, dto)

        # Assert
        assert result == updated_job
        assert mock_job_repository.get_by_id.call_count == 1
        mock_job_repository.update.assert_called_once()

    def test_update_job_not_found_before_update(self):
        """Test updating job when job doesn't exist (checked before update)"""
        # Arrange
        account_id = uuid4()
        job_id = uuid4()
        mock_job_repository = MagicMock(spec=IJobRepository)
        mock_job_repository.get_by_id.return_value = None

        service = JobService(mock_job_repository)
        dto = UpdateJobDto(title="Updated Title")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.update_job(account_id, job_id, dto)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Job not found" in str(exc_info.value.detail)
        mock_job_repository.get_by_id.assert_called_once_with(job_id)
        mock_job_repository.update.assert_not_called()

    def test_update_job_not_found_after_update(self):
        """Test updating job when update returns None (race condition scenario)"""
        # Arrange
        account_id = uuid4()
        job_id = uuid4()
        original_job = Job(
            id=job_id,
            account_id=account_id,
            title="Original Title",
            description="Original description",
            budget=1000.0,
            location="Original Location",
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=7),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        mock_job_repository = MagicMock(spec=IJobRepository)
        # First call returns job, but update returns None (simulating race condition)
        mock_job_repository.get_by_id.return_value = original_job
        mock_job_repository.update.return_value = None

        service = JobService(mock_job_repository)
        dto = UpdateJobDto(title="Updated Title")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.update_job(account_id, job_id, dto)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Job not found" in str(exc_info.value.detail)
        mock_job_repository.get_by_id.assert_called_once_with(job_id)
        mock_job_repository.update.assert_called_once()

    def test_update_job_unauthorized(self):
        """Test updating job when job belongs to different account"""
        # Arrange
        account_id = uuid4()
        other_account_id = uuid4()
        job_id = uuid4()
        mock_job = Job(
            id=job_id,
            account_id=other_account_id,  # Different account
            title="Test Job",
            description="Test description",
            budget=1000.0,
            location="Test Location",
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=7),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        mock_job_repository = MagicMock(spec=IJobRepository)
        mock_job_repository.get_by_id.return_value = mock_job

        service = JobService(mock_job_repository)
        dto = UpdateJobDto(title="Updated Title")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.update_job(account_id, job_id, dto)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "not authorized" in str(exc_info.value.detail).lower()
        mock_job_repository.get_by_id.assert_called_once_with(job_id)
        mock_job_repository.update.assert_not_called()


class TestJobServiceDeleteJob:
    """Tests for JobService.delete_job"""

    def test_delete_job_success(self):
        """Test deleting job successfully"""
        # Arrange
        account_id = uuid4()
        job_id = uuid4()
        mock_job = Job(
            id=job_id,
            account_id=account_id,
            title="Test Job",
            description="Test description",
            budget=1000.0,
            location="Test Location",
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=7),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        mock_job_repository = MagicMock(spec=IJobRepository)
        mock_job_repository.get_by_id.return_value = mock_job
        mock_job_repository.delete.return_value = True

        service = JobService(mock_job_repository)

        # Act
        result = service.delete_job(account_id, job_id)

        # Assert
        assert result is True
        mock_job_repository.get_by_id.assert_called_once_with(job_id)
        mock_job_repository.delete.assert_called_once_with(job_id)

    def test_delete_job_not_found(self):
        """Test deleting job when job doesn't exist"""
        # Arrange
        account_id = uuid4()
        job_id = uuid4()
        mock_job_repository = MagicMock(spec=IJobRepository)
        mock_job_repository.get_by_id.return_value = None

        service = JobService(mock_job_repository)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.delete_job(account_id, job_id)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Job not found" in str(exc_info.value.detail)
        mock_job_repository.get_by_id.assert_called_once_with(job_id)
        mock_job_repository.delete.assert_not_called()

    def test_delete_job_unauthorized(self):
        """Test deleting job when job belongs to different account"""
        # Arrange
        account_id = uuid4()
        other_account_id = uuid4()
        job_id = uuid4()
        mock_job = Job(
            id=job_id,
            account_id=other_account_id,  # Different account
            title="Test Job",
            description="Test description",
            budget=1000.0,
            location="Test Location",
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=7),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        mock_job_repository = MagicMock(spec=IJobRepository)
        mock_job_repository.get_by_id.return_value = mock_job

        service = JobService(mock_job_repository)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.delete_job(account_id, job_id)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "not authorized" in str(exc_info.value.detail).lower()
        mock_job_repository.get_by_id.assert_called_once_with(job_id)
        mock_job_repository.delete.assert_not_called()
