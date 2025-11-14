from unittest.mock import MagicMock
from uuid import uuid4

from app.domain.models.account import Account, AccountType
from app.domain.repositories.interfaces.account import IAccountRepository
from app.domain.repositories.interfaces.application import IApplicationRepository
from app.domain.repositories.interfaces.job import IJobRepository
from app.services.application import ApplicationService


class TestApplicationServiceGetEmployerAccounts:
    """Tests for ApplicationService._get_employer_accounts"""

    def test_get_employer_accounts_returns_empty_list_when_no_accounts(self):
        """Test _get_employer_accounts returns empty list when user has no employer accounts"""
        # Arrange
        user_id = uuid4()

        mock_application_repository = MagicMock(spec=IApplicationRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)
        mock_job_repository = MagicMock(spec=IJobRepository)

        mock_account_repository.get_user_accounts.return_value = []

        service = ApplicationService(
            mock_application_repository, mock_account_repository, mock_job_repository
        )

        # Act
        result = service._get_employer_accounts(user_id)

        # Assert
        assert result == []
        assert isinstance(result, list) or hasattr(result, "__iter__")
        mock_account_repository.get_user_accounts.assert_called_once_with(
            user_id, AccountType.EMPLOYER
        )

    def test_get_employer_accounts_returns_single_account(self):
        """Test _get_employer_accounts returns a single employer account"""
        # Arrange
        user_id = uuid4()
        account_id = uuid4()

        employer_account = Account(
            id=account_id,
            user_id=user_id,
            name="Test Employer",
            account_type=AccountType.EMPLOYER,
            is_active=True,
        )

        mock_application_repository = MagicMock(spec=IApplicationRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)
        mock_job_repository = MagicMock(spec=IJobRepository)

        mock_account_repository.get_user_accounts.return_value = [employer_account]

        service = ApplicationService(
            mock_application_repository, mock_account_repository, mock_job_repository
        )

        # Act
        result = service._get_employer_accounts(user_id)

        # Assert
        assert len(result) == 1
        assert result[0].id == account_id
        assert result[0].account_type == AccountType.EMPLOYER
        assert result[0].user_id == user_id
        mock_account_repository.get_user_accounts.assert_called_once_with(
            user_id, AccountType.EMPLOYER
        )

    def test_get_employer_accounts_returns_multiple_accounts(self):
        """Test _get_employer_accounts returns multiple employer accounts"""
        # Arrange
        user_id = uuid4()
        account_id1 = uuid4()
        account_id2 = uuid4()
        account_id3 = uuid4()

        employer_account1 = Account(
            id=account_id1,
            user_id=user_id,
            name="Employer Account 1",
            account_type=AccountType.EMPLOYER,
            is_active=True,
        )
        employer_account2 = Account(
            id=account_id2,
            user_id=user_id,
            name="Employer Account 2",
            account_type=AccountType.EMPLOYER,
            is_active=True,
        )
        employer_account3 = Account(
            id=account_id3,
            user_id=user_id,
            name="Employer Account 3",
            account_type=AccountType.EMPLOYER,
            is_active=True,
        )

        mock_application_repository = MagicMock(spec=IApplicationRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)
        mock_job_repository = MagicMock(spec=IJobRepository)

        mock_account_repository.get_user_accounts.return_value = [
            employer_account1,
            employer_account2,
            employer_account3,
        ]

        service = ApplicationService(
            mock_application_repository, mock_account_repository, mock_job_repository
        )

        # Act
        result = service._get_employer_accounts(user_id)

        # Assert
        assert len(result) == 3
        account_ids = {acc.id for acc in result}
        assert account_id1 in account_ids
        assert account_id2 in account_ids
        assert account_id3 in account_ids

        # Verify all accounts are EMPLOYER type
        for account in result:
            assert account.account_type == AccountType.EMPLOYER
            assert account.user_id == user_id

        mock_account_repository.get_user_accounts.assert_called_once_with(
            user_id, AccountType.EMPLOYER
        )

    def test_get_employer_accounts_filters_only_employer_type(self):
        """Test _get_employer_accounts only returns EMPLOYER type accounts (repository filters)"""
        # Arrange
        user_id = uuid4()
        account_id1 = uuid4()
        account_id2 = uuid4()

        # Repository should only return EMPLOYER accounts
        employer_account1 = Account(
            id=account_id1,
            user_id=user_id,
            name="Employer Account 1",
            account_type=AccountType.EMPLOYER,
            is_active=True,
        )
        employer_account2 = Account(
            id=account_id2,
            user_id=user_id,
            name="Employer Account 2",
            account_type=AccountType.EMPLOYER,
            is_active=True,
        )

        mock_application_repository = MagicMock(spec=IApplicationRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)
        mock_job_repository = MagicMock(spec=IJobRepository)

        # Repository filters by AccountType.EMPLOYER
        mock_account_repository.get_user_accounts.return_value = [
            employer_account1,
            employer_account2,
        ]

        service = ApplicationService(
            mock_application_repository, mock_account_repository, mock_job_repository
        )

        # Act
        result = service._get_employer_accounts(user_id)

        # Assert
        assert len(result) == 2
        for account in result:
            assert account.account_type == AccountType.EMPLOYER

        # Verify repository was called with EMPLOYER filter
        mock_account_repository.get_user_accounts.assert_called_once_with(
            user_id, AccountType.EMPLOYER
        )

    def test_get_employer_accounts_includes_inactive_accounts(self):
        """Test _get_employer_accounts includes inactive employer accounts if repository returns them"""
        # Arrange
        user_id = uuid4()
        active_account_id = uuid4()
        inactive_account_id = uuid4()

        active_account = Account(
            id=active_account_id,
            user_id=user_id,
            name="Active Employer",
            account_type=AccountType.EMPLOYER,
            is_active=True,
        )
        inactive_account = Account(
            id=inactive_account_id,
            user_id=user_id,
            name="Inactive Employer",
            account_type=AccountType.EMPLOYER,
            is_active=False,
        )

        mock_application_repository = MagicMock(spec=IApplicationRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)
        mock_job_repository = MagicMock(spec=IJobRepository)

        mock_account_repository.get_user_accounts.return_value = [
            active_account,
            inactive_account,
        ]

        service = ApplicationService(
            mock_application_repository, mock_account_repository, mock_job_repository
        )

        # Act
        result = service._get_employer_accounts(user_id)

        # Assert
        assert len(result) == 2
        account_ids = {acc.id for acc in result}
        assert active_account_id in account_ids
        assert inactive_account_id in account_ids

        # Verify both active and inactive accounts are returned
        active_accounts = [acc for acc in result if acc.is_active]
        inactive_accounts = [acc for acc in result if not acc.is_active]
        assert len(active_accounts) == 1
        assert len(inactive_accounts) == 1

        mock_account_repository.get_user_accounts.assert_called_once_with(
            user_id, AccountType.EMPLOYER
        )

    def test_get_employer_accounts_with_different_user_ids(self):
        """Test _get_employer_accounts works correctly with different user IDs"""
        # Arrange
        user_id1 = uuid4()
        user_id2 = uuid4()
        account_id1 = uuid4()
        account_id2 = uuid4()

        employer_account1 = Account(
            id=account_id1,
            user_id=user_id1,
            name="User 1 Employer",
            account_type=AccountType.EMPLOYER,
            is_active=True,
        )
        employer_account2 = Account(
            id=account_id2,
            user_id=user_id2,
            name="User 2 Employer",
            account_type=AccountType.EMPLOYER,
            is_active=True,
        )

        mock_application_repository = MagicMock(spec=IApplicationRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)
        mock_job_repository = MagicMock(spec=IJobRepository)

        # Setup different return values for different user IDs
        def get_user_accounts_side_effect(user_id, account_type):
            if user_id == user_id1:
                return [employer_account1]
            elif user_id == user_id2:
                return [employer_account2]
            return []

        mock_account_repository.get_user_accounts.side_effect = get_user_accounts_side_effect

        service = ApplicationService(
            mock_application_repository, mock_account_repository, mock_job_repository
        )

        # Act
        result1 = service._get_employer_accounts(user_id1)
        result2 = service._get_employer_accounts(user_id2)

        # Assert
        assert len(result1) == 1
        assert result1[0].id == account_id1
        assert result1[0].user_id == user_id1

        assert len(result2) == 1
        assert result2[0].id == account_id2
        assert result2[0].user_id == user_id2

        # Verify repository was called twice with different user IDs
        assert mock_account_repository.get_user_accounts.call_count == 2

    def test_get_employer_accounts_returns_sequence_type(self):
        """Test _get_employer_accounts returns a Sequence type"""
        # Arrange
        user_id = uuid4()
        account_id = uuid4()

        employer_account = Account(
            id=account_id,
            user_id=user_id,
            name="Test Employer",
            account_type=AccountType.EMPLOYER,
            is_active=True,
        )

        mock_application_repository = MagicMock(spec=IApplicationRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)
        mock_job_repository = MagicMock(spec=IJobRepository)

        mock_account_repository.get_user_accounts.return_value = [employer_account]

        service = ApplicationService(
            mock_application_repository, mock_account_repository, mock_job_repository
        )

        # Act
        result = service._get_employer_accounts(user_id)

        # Assert
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__len__")
        # Should be able to convert to list
        result_list = list(result)
        assert isinstance(result_list, list)

    def test_get_employer_accounts_with_various_account_names(self):
        """Test _get_employer_accounts handles accounts with different names"""
        # Arrange
        user_id = uuid4()
        account_id1 = uuid4()
        account_id2 = uuid4()
        account_id3 = uuid4()

        employer_account1 = Account(
            id=account_id1,
            user_id=user_id,
            name="Company A",
            account_type=AccountType.EMPLOYER,
            is_active=True,
        )
        employer_account2 = Account(
            id=account_id2,
            user_id=user_id,
            name="Real Estate Agency",
            account_type=AccountType.EMPLOYER,
            is_active=True,
        )
        employer_account3 = Account(
            id=account_id3,
            user_id=user_id,
            name="Photography Studio",
            account_type=AccountType.EMPLOYER,
            is_active=True,
        )

        mock_application_repository = MagicMock(spec=IApplicationRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)
        mock_job_repository = MagicMock(spec=IJobRepository)

        mock_account_repository.get_user_accounts.return_value = [
            employer_account1,
            employer_account2,
            employer_account3,
        ]

        service = ApplicationService(
            mock_application_repository, mock_account_repository, mock_job_repository
        )

        # Act
        result = service._get_employer_accounts(user_id)

        # Assert
        assert len(result) == 3
        account_names = {acc.name for acc in result}
        assert "Company A" in account_names
        assert "Real Estate Agency" in account_names
        assert "Photography Studio" in account_names

    def test_get_employer_accounts_consistency(self):
        """Test _get_employer_accounts returns consistent results on multiple calls"""
        # Arrange
        user_id = uuid4()
        account_id = uuid4()

        employer_account = Account(
            id=account_id,
            user_id=user_id,
            name="Test Employer",
            account_type=AccountType.EMPLOYER,
            is_active=True,
        )

        mock_application_repository = MagicMock(spec=IApplicationRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)
        mock_job_repository = MagicMock(spec=IJobRepository)

        mock_account_repository.get_user_accounts.return_value = [employer_account]

        service = ApplicationService(
            mock_application_repository, mock_account_repository, mock_job_repository
        )

        # Act - call multiple times
        result1 = service._get_employer_accounts(user_id)
        result2 = service._get_employer_accounts(user_id)
        result3 = service._get_employer_accounts(user_id)

        # Assert - should return consistent results
        assert len(result1) == len(result2) == len(result3) == 1
        assert result1[0].id == result2[0].id == result3[0].id == account_id

        # Verify repository was called three times
        assert mock_account_repository.get_user_accounts.call_count == 3

    def test_get_employer_accounts_passes_correct_account_type(self):
        """Test _get_employer_accounts passes AccountType.EMPLOYER to repository"""
        # Arrange
        user_id = uuid4()

        mock_application_repository = MagicMock(spec=IApplicationRepository)
        mock_account_repository = MagicMock(spec=IAccountRepository)
        mock_job_repository = MagicMock(spec=IJobRepository)

        mock_account_repository.get_user_accounts.return_value = []

        service = ApplicationService(
            mock_application_repository, mock_account_repository, mock_job_repository
        )

        # Act
        service._get_employer_accounts(user_id)

        # Assert - verify the exact arguments passed to the repository
        mock_account_repository.get_user_accounts.assert_called_once()
        call_args = mock_account_repository.get_user_accounts.call_args
        assert call_args[0][0] == user_id
        assert call_args[0][1] == AccountType.EMPLOYER
