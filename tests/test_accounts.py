from uuid import uuid4

from fastapi import status

from tests.utils import create_test_account, create_test_user, get_auth_headers


class TestCreateAccount:
    """Tests for POST /accounts/"""

    def test_create_account_success_employer(self, client, db_session):
        """Test creating an employer account successfully"""
        user = create_test_user(db_session)
        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        account_data = {
            "name": "My Company",
            "account_type": "EMPLOYER",
        }

        response = client.post("/accounts/", json=account_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == account_data["name"]
        assert data["account_type"] == account_data["account_type"]
        assert data["user_id"] == str(user.id)
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_account_success_droner(self, client, db_session):
        """Test creating a droner account successfully"""
        user = create_test_user(db_session)
        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        account_data = {
            "name": "My Drone Business",
            "account_type": "DRONER",
        }

        response = client.post("/accounts/", json=account_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == account_data["name"]
        assert data["account_type"] == account_data["account_type"]
        assert data["user_id"] == str(user.id)

    def test_create_account_multiple_employers(self, client, db_session):
        """Test creating multiple employer accounts (allowed)"""
        user = create_test_user(db_session)
        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        # Create first employer account
        account_data_1 = {
            "name": "Company 1",
            "account_type": "EMPLOYER",
        }
        response1 = client.post("/accounts/", json=account_data_1, headers=headers)
        assert response1.status_code == status.HTTP_201_CREATED

        # Create second employer account (should be allowed)
        account_data_2 = {
            "name": "Company 2",
            "account_type": "EMPLOYER",
        }
        response2 = client.post("/accounts/", json=account_data_2, headers=headers)
        assert response2.status_code == status.HTTP_201_CREATED
        assert response2.json()["name"] == account_data_2["name"]

    def test_create_account_duplicate_droner(self, client, db_session):
        """Test creating a second droner account (should fail)"""
        user = create_test_user(db_session)
        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        # Create first droner account
        account_data_1 = {
            "name": "Drone Business 1",
            "account_type": "DRONER",
        }
        response1 = client.post("/accounts/", json=account_data_1, headers=headers)
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to create second droner account (should fail)
        account_data_2 = {
            "name": "Drone Business 2",
            "account_type": "DRONER",
        }
        response2 = client.post("/accounts/", json=account_data_2, headers=headers)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "one droner account" in response2.json()["detail"].lower()

    def test_create_account_unauthenticated(self, client):
        """Test creating an account without authentication"""
        account_data = {
            "name": "My Company",
            "account_type": "EMPLOYER",
        }

        response = client.post("/accounts/", json=account_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_account_invalid_token(self, client):
        """Test creating an account with invalid token"""
        headers = get_auth_headers("invalid_token")
        account_data = {
            "name": "My Company",
            "account_type": "EMPLOYER",
        }

        response = client.post("/accounts/", json=account_data, headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_account_missing_fields(self, client, db_session):
        """Test creating an account with missing required fields"""
        user = create_test_user(db_session)
        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        account_data = {
            "name": "My Company",
            # Missing account_type
        }

        response = client.post("/accounts/", json=account_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_account_empty_name(self, client, db_session):
        """Test creating an account with empty name"""
        user = create_test_user(db_session)
        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        account_data = {
            "name": "",
            "account_type": "EMPLOYER",
        }

        response = client.post("/accounts/", json=account_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetUserAccounts:
    """Tests for GET /accounts/"""

    def test_get_user_accounts_success(self, client, db_session):
        """Test getting all accounts for a user"""
        user = create_test_user(db_session)
        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        # Create multiple accounts
        account1 = create_test_account(db_session, user.id, name="Account 1")
        account2 = create_test_account(db_session, user.id, name="Account 2")

        response = client.get("/accounts/", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

        # Verify account structure
        account_ids = [acc["id"] for acc in data]
        assert str(account1.id) in account_ids
        assert str(account2.id) in account_ids

        # Verify each account has required fields
        for account in data:
            assert "id" in account
            assert "name" in account
            assert "account_type" in account
            assert "user_id" in account
            assert "is_active" in account

    def test_get_user_accounts_empty(self, client, db_session):
        """Test getting accounts when user has none"""
        user = create_test_user(db_session)
        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        response = client.get("/accounts/", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # Should be empty or contain accounts from previous tests (depending on isolation)

    def test_get_user_accounts_unauthenticated(self, client):
        """Test getting accounts without authentication"""
        response = client.get("/accounts/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_user_accounts_only_own(self, client, db_session):
        """Test that users only see their own accounts"""
        user1 = create_test_user(db_session, email="user1@test.com")
        user2 = create_test_user(db_session, email="user2@test.com")

        # Signin to get a token for user1
        signin_response = client.post(
            "/auth/signin",
            json={"email": user1.email, "password": "testpassword123"},
        )
        token1 = signin_response.json()["access_token"]
        headers1 = get_auth_headers(token1)

        # Create account for user1
        account1 = create_test_account(db_session, user1.id, name="User1 Account")
        # Create account for user2
        account2 = create_test_account(db_session, user2.id, name="User2 Account")

        # User1 should only see their own account
        response = client.get("/accounts/", headers=headers1)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        account_ids = [acc["id"] for acc in data]
        assert str(account1.id) in account_ids
        assert str(account2.id) not in account_ids


class TestGetAccount:
    """Tests for GET /accounts/{account_id}"""

    def test_get_account_success(self, client, db_session):
        """Test getting a specific account by ID"""
        user = create_test_user(db_session)
        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        account = create_test_account(db_session, user.id, name="My Account")

        response = client.get(f"/accounts/{account.id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(account.id)
        assert data["name"] == account.name
        assert data["user_id"] == str(user.id)
        # Access account_type via getattr to avoid type checker issues with SQLModel FieldInfo
        account_type_value = getattr(account, "account_type").value
        assert data["account_type"] == account_type_value

    def test_get_account_not_found(self, client, db_session):
        """Test getting a non-existent account"""
        user = create_test_user(db_session)
        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        fake_account_id = uuid4()
        response = client.get(f"/accounts/{fake_account_id}", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_account_unauthorized(self, client, db_session):
        """Test getting another user's account (should return 403)"""
        user1 = create_test_user(db_session, email="user1@test.com")
        user2 = create_test_user(db_session, email="user2@test.com")

        # Signin to get a token for user1
        signin_response = client.post(
            "/auth/signin",
            json={"email": user1.email, "password": "testpassword123"},
        )
        token1 = signin_response.json()["access_token"]
        headers1 = get_auth_headers(token1)

        # Create account for user2
        account2 = create_test_account(db_session, user2.id, name="User2 Account")

        # User1 tries to access user2's account
        response = client.get(f"/accounts/{account2.id}", headers=headers1)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "not authorized" in response.json()["detail"].lower()

    def test_get_account_unauthenticated(self, client, db_session):
        """Test getting an account without authentication"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        response = client.get(f"/accounts/{account.id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_account_invalid_uuid(self, client, db_session):
        """Test getting an account with invalid UUID format"""
        user = create_test_user(db_session)
        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        response = client.get("/accounts/invalid-uuid", headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUpdateAccount:
    """Tests for PUT /accounts/{account_id}"""

    def test_update_account_success(self, client, db_session):
        """Test updating an account successfully"""
        user = create_test_user(db_session)
        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        account = create_test_account(db_session, user.id, name="Original Name")

        update_data = {
            "name": "Updated Name",
        }

        response = client.put(
            f"/accounts/{account.id}", json=update_data, headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["id"] == str(account.id)
        assert data["user_id"] == str(user.id)

    def test_update_account_partial(self, client, db_session):
        """Test updating an account with partial data (only name)"""
        user = create_test_user(db_session)
        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        account = create_test_account(db_session, user.id, name="Original Name")

        # Update only name (partial update)
        update_data = {"name": "Updated Name"}

        response = client.put(
            f"/accounts/{account.id}", json=update_data, headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["id"] == str(account.id)
        # Other fields should remain unchanged
        # Access account_type via getattr to avoid type checker issues with SQLModel FieldInfo
        account_type_value = getattr(account, "account_type").value
        assert data["account_type"] == account_type_value

    def test_update_account_not_found(self, client, db_session):
        """Test updating a non-existent account"""
        user = create_test_user(db_session)
        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        fake_account_id = uuid4()
        update_data = {"name": "Updated Name"}

        response = client.put(
            f"/accounts/{fake_account_id}", json=update_data, headers=headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_update_account_unauthorized(self, client, db_session):
        """Test updating another user's account (should return 403)"""
        user1 = create_test_user(db_session, email="user1@test.com")
        user2 = create_test_user(db_session, email="user2@test.com")

        # Signin to get a token for user1
        signin_response = client.post(
            "/auth/signin",
            json={"email": user1.email, "password": "testpassword123"},
        )
        token1 = signin_response.json()["access_token"]
        headers1 = get_auth_headers(token1)

        # Create account for user2
        account2 = create_test_account(db_session, user2.id, name="User2 Account")

        # User1 tries to update user2's account
        update_data = {"name": "Hacked Name"}
        response = client.put(
            f"/accounts/{account2.id}", json=update_data, headers=headers1
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "not authorized" in response.json()["detail"].lower()

    def test_update_account_unauthenticated(self, client, db_session):
        """Test updating an account without authentication"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        update_data = {"name": "Updated Name"}
        response = client.put(f"/accounts/{account.id}", json=update_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_account_empty_name(self, client, db_session):
        """Test updating an account with empty name (should fail validation)"""
        user = create_test_user(db_session)
        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        account = create_test_account(db_session, user.id, name="Original Name")

        update_data = {"name": ""}

        response = client.put(
            f"/accounts/{account.id}", json=update_data, headers=headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
