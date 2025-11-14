from uuid import uuid4

from app.domain.models.account import AccountType, AccountUpdate
from app.domain.repositories.account import AccountRepository
from tests.utils import create_test_account, create_test_user


class TestAccountRepositoryGetAll:
    """Tests for AccountRepository.get_all"""

    def test_get_all_no_accounts(self, db_session):
        """Test getting all accounts when there are none"""
        # Arrange
        repository = AccountRepository(db_session)

        # Act
        accounts = repository.get_all()

        # Assert
        assert len(accounts) == 0
        assert isinstance(accounts, list) or hasattr(accounts, "__iter__")

    def test_get_all_single_account(self, db_session):
        """Test getting all accounts when there is one account"""
        # Arrange
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id, name="Test Account")

        repository = AccountRepository(db_session)

        # Act
        accounts = repository.get_all()

        # Assert
        assert len(accounts) == 1
        assert accounts[0].id == account.id
        assert accounts[0].name == account.name
        assert accounts[0].user_id == user.id

    def test_get_all_multiple_accounts_same_user(self, db_session):
        """Test getting all accounts when there are multiple accounts for the same user"""
        # Arrange
        user = create_test_user(db_session)
        account1 = create_test_account(
            db_session, user.id, name="Account 1", account_type=AccountType.EMPLOYER
        )
        account2 = create_test_account(
            db_session, user.id, name="Account 2", account_type=AccountType.DRONER
        )
        account3 = create_test_account(
            db_session, user.id, name="Account 3", account_type=AccountType.EMPLOYER
        )

        repository = AccountRepository(db_session)

        # Act
        accounts = repository.get_all()

        # Assert
        assert len(accounts) == 3
        account_ids = {acc.id for acc in accounts}
        assert account1.id in account_ids
        assert account2.id in account_ids
        assert account3.id in account_ids

    def test_get_all_multiple_accounts_different_users(self, db_session):
        """Test getting all accounts when there are multiple accounts for different users"""
        # Arrange
        user1 = create_test_user(db_session, email="user1@test.com")
        user2 = create_test_user(db_session, email="user2@test.com")
        user3 = create_test_user(db_session, email="user3@test.com")

        account1 = create_test_account(
            db_session, user1.id, name="User1 Account", account_type=AccountType.EMPLOYER
        )
        account2 = create_test_account(
            db_session, user2.id, name="User2 Account", account_type=AccountType.DRONER
        )
        account3 = create_test_account(
            db_session, user3.id, name="User3 Account", account_type=AccountType.EMPLOYER
        )

        repository = AccountRepository(db_session)

        # Act
        accounts = repository.get_all()

        # Assert
        assert len(accounts) == 3
        account_ids = {acc.id for acc in accounts}
        assert account1.id in account_ids
        assert account2.id in account_ids
        assert account3.id in account_ids

    def test_get_all_includes_inactive_accounts(self, db_session):
        """Test that get_all includes inactive accounts"""
        # Arrange
        user = create_test_user(db_session)
        active_account = create_test_account(
            db_session, user.id, name="Active Account", is_active=True
        )
        inactive_account = create_test_account(
            db_session, user.id, name="Inactive Account", is_active=False
        )

        repository = AccountRepository(db_session)

        # Act
        accounts = repository.get_all()

        # Assert
        assert len(accounts) == 2
        account_ids = {acc.id for acc in accounts}
        assert active_account.id in account_ids
        assert inactive_account.id in account_ids

    def test_get_all_includes_all_account_types(self, db_session):
        """Test that get_all includes both EMPLOYER and DRONER account types"""
        # Arrange
        user = create_test_user(db_session)
        employer_account = create_test_account(
            db_session, user.id, name="Employer Account", account_type=AccountType.EMPLOYER
        )
        droner_account = create_test_account(
            db_session, user.id, name="Droner Account", account_type=AccountType.DRONER
        )

        repository = AccountRepository(db_session)

        # Act
        accounts = repository.get_all()

        # Assert
        assert len(accounts) == 2
        account_ids = {acc.id for acc in accounts}
        assert employer_account.id in account_ids
        assert droner_account.id in account_ids

        # Verify account types
        account_types = {acc.account_type for acc in accounts}
        assert AccountType.EMPLOYER in account_types
        assert AccountType.DRONER in account_types

    def test_get_all_returns_sequence(self, db_session):
        """Test that get_all returns a Sequence type"""
        # Arrange
        user = create_test_user(db_session)
        create_test_account(db_session, user.id)

        repository = AccountRepository(db_session)

        # Act
        accounts = repository.get_all()

        # Assert
        assert hasattr(accounts, "__iter__")
        assert hasattr(accounts, "__len__")
        # Should be able to convert to list
        accounts_list = list(accounts)
        assert isinstance(accounts_list, list)


class TestAccountRepositoryUpdate:
    """Tests for AccountRepository.update"""

    def test_update_account_success(self, db_session):
        """Test updating an account successfully"""
        # Arrange
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id, name="Original Name")

        repository = AccountRepository(db_session)
        update_data = AccountUpdate(name="Updated Name")

        # Act
        result = repository.update(account.id, update_data)

        # Assert
        assert result is not None
        assert result.id == account.id
        assert result.name == "Updated Name"

    def test_update_account_not_found(self, db_session):
        """Test updating an account that doesn't exist"""
        # Arrange
        repository = AccountRepository(db_session)
        non_existent_id = uuid4()
        update_data = AccountUpdate(name="Updated Name")

        # Act
        result = repository.update(non_existent_id, update_data)

        # Assert
        assert result is None
