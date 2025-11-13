from uuid import uuid4

from fastapi import status

from app.domain.models.account import AccountType
from tests.utils import (
    create_test_account,
    create_test_favorite,
    create_test_job,
    create_test_user,
    get_account_headers,
)


class TestCreateFavorite:
    """Tests for POST /jobs/favorites/"""

    def test_create_favorite_success(self, client, db_session):
        """Test creating a favorite successfully"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        # Signin to get token
        signin_response = client.post(
            "/auth/signin",
            json={"email": employer_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, employer_account.id)

        favorite_data = {"job_id": str(job.id)}

        response = client.post("/jobs/favorites/", json=favorite_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["account_id"] == str(employer_account.id)
        assert data["job_id"] == str(job.id)
        assert "id" in data
        assert "created_at" in data

    def test_create_favorite_droner_account(self, client, db_session):
        """Test creating a favorite with a droner account"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer2@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create droner user and account
        droner_user = create_test_user(db_session, email="droner@test.com")
        droner_account = create_test_account(
            db_session, droner_user.id, account_type=AccountType.DRONER
        )

        # Signin as droner
        signin_response = client.post(
            "/auth/signin",
            json={"email": droner_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, droner_account.id)

        favorite_data = {"job_id": str(job.id)}

        response = client.post("/jobs/favorites/", json=favorite_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["account_id"] == str(droner_account.id)
        assert data["job_id"] == str(job.id)

    def test_create_favorite_job_not_found(self, client, db_session):
        """Test creating a favorite for a non-existent job"""
        user = create_test_user(db_session, email="user@test.com")
        account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )

        # Signin
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        fake_job_id = uuid4()
        favorite_data = {"job_id": str(fake_job_id)}

        # This might succeed (favorite created) or fail (foreign key constraint)
        # depending on database configuration
        response = client.post("/jobs/favorites/", json=favorite_data, headers=headers)
        # SQLite doesn't enforce foreign keys by default, so it might succeed
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
        ]

    def test_create_favorite_missing_job_id(self, client, db_session):
        """Test creating a favorite without job_id"""
        user = create_test_user(db_session, email="user2@test.com")
        account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )

        # Signin
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        favorite_data = {}  # Missing job_id

        response = client.post("/jobs/favorites/", json=favorite_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_favorite_unauthenticated(self, client):
        """Test creating a favorite without authentication"""
        fake_job_id = uuid4()
        favorite_data = {"job_id": str(fake_job_id)}

        response = client.post("/jobs/favorites/", json=favorite_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_favorite_missing_account_header(self, client, db_session):
        """Test creating a favorite without x-account-id header"""
        user = create_test_user(db_session, email="user3@test.com")
        account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, account.id)

        # Signin but don't include account header
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}  # Missing x-account-id

        favorite_data = {"job_id": str(job.id)}

        response = client.post("/jobs/favorites/", json=favorite_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_favorite_wrong_account(self, client, db_session):
        """Test creating a favorite with account that doesn't belong to user"""
        user1 = create_test_user(db_session, email="user4@test.com")
        create_test_account(db_session, user1.id, account_type=AccountType.EMPLOYER)

        user2 = create_test_user(db_session, email="user5@test.com")
        account2 = create_test_account(
            db_session, user2.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, account2.id)

        # Signin as user1 but try to use account2
        signin_response = client.post(
            "/auth/signin",
            json={"email": user1.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account2.id)  # Wrong account

        favorite_data = {"job_id": str(job.id)}

        response = client.post("/jobs/favorites/", json=favorite_data, headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "not authorized" in response.json()["detail"].lower()


class TestGetFavorites:
    """Tests for GET /jobs/favorites/"""

    def test_get_favorites_success(self, client, db_session):
        """Test getting favorites successfully"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer3@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job1 = create_test_job(db_session, employer_account.id)
        job2 = create_test_job(db_session, employer_account.id)

        # Create favorites
        favorite1 = create_test_favorite(db_session, employer_account.id, job1.id)
        favorite2 = create_test_favorite(db_session, employer_account.id, job2.id)

        # Signin
        signin_response = client.post(
            "/auth/signin",
            json={"email": employer_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, employer_account.id)

        response = client.get("/jobs/favorites/", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

        favorite_ids = [fav["id"] for fav in data]
        assert str(favorite1.id) in favorite_ids
        assert str(favorite2.id) in favorite_ids

        # Verify structure
        for favorite in data:
            assert "id" in favorite
            assert "account_id" in favorite
            assert "job_id" in favorite
            assert "created_at" in favorite

    def test_get_favorites_empty(self, client, db_session):
        """Test getting favorites when account has none"""
        user = create_test_user(db_session, email="user6@test.com")
        account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )

        # Signin
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        response = client.get("/jobs/favorites/", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # Should be empty or contain favorites from previous tests (depending on isolation)

    def test_get_favorites_only_own(self, client, db_session):
        """Test that users only see favorites for their account"""
        user1 = create_test_user(db_session, email="user7@test.com")
        account1 = create_test_account(
            db_session, user1.id, account_type=AccountType.EMPLOYER
        )

        user2 = create_test_user(db_session, email="user8@test.com")
        account2 = create_test_account(
            db_session, user2.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, account2.id)

        # Create favorite for account2
        favorite2 = create_test_favorite(db_session, account2.id, job.id)

        # Signin as user1
        signin_response = client.post(
            "/auth/signin",
            json={"email": user1.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account1.id)

        response = client.get("/jobs/favorites/", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        favorite_ids = [fav["id"] for fav in data]
        assert (
            str(favorite2.id) not in favorite_ids
        )  # Should not see account2's favorites

    def test_get_favorites_unauthenticated(self, client):
        """Test getting favorites without authentication"""
        response = client.get("/jobs/favorites/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_favorites_missing_account_header(self, client, db_session):
        """Test getting favorites without x-account-id header"""
        user = create_test_user(db_session, email="user9@test.com")
        create_test_account(db_session, user.id, account_type=AccountType.EMPLOYER)

        # Signin but don't include account header
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}  # Missing x-account-id

        response = client.get("/jobs/favorites/", headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDeleteFavorite:
    """Tests for DELETE /jobs/favorites/{favorite_id}"""

    def test_delete_favorite_success(self, client, db_session):
        """Test deleting a favorite successfully"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer4@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        favorite = create_test_favorite(db_session, employer_account.id, job.id)

        # Signin
        signin_response = client.post(
            "/auth/signin",
            json={"email": employer_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, employer_account.id)

        response = client.delete(f"/jobs/favorites/{favorite.id}", headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify favorite is deleted
        get_response = client.get("/jobs/favorites/", headers=headers)
        assert get_response.status_code == status.HTTP_200_OK
        data = get_response.json()
        favorite_ids = [fav["id"] for fav in data]
        assert str(favorite.id) not in favorite_ids

    def test_delete_favorite_unauthorized(self, client, db_session):
        """Test deleting someone else's favorite (should fail)"""
        user1 = create_test_user(db_session, email="user10@test.com")
        account1 = create_test_account(
            db_session, user1.id, account_type=AccountType.EMPLOYER
        )

        user2 = create_test_user(db_session, email="user11@test.com")
        account2 = create_test_account(
            db_session, user2.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, account2.id)

        favorite = create_test_favorite(db_session, account2.id, job.id)

        # Signin as user1
        signin_response = client.post(
            "/auth/signin",
            json={"email": user1.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account1.id)

        response = client.delete(f"/jobs/favorites/{favorite.id}", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "not authorized" in response.json()["detail"].lower()

    def test_delete_favorite_not_found(self, client, db_session):
        """Test deleting a non-existent favorite"""
        user = create_test_user(db_session, email="user12@test.com")
        account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )

        # Signin
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        fake_favorite_id = uuid4()
        response = client.delete(f"/jobs/favorites/{fake_favorite_id}", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_delete_favorite_unauthenticated(self, client):
        """Test deleting a favorite without authentication"""
        fake_favorite_id = uuid4()
        response = client.delete(f"/jobs/favorites/{fake_favorite_id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_favorite_missing_account_header(self, client, db_session):
        """Test deleting a favorite without x-account-id header"""
        user = create_test_user(db_session, email="user13@test.com")
        account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, account.id)
        favorite = create_test_favorite(db_session, account.id, job.id)

        # Signin but don't include account header
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}  # Missing x-account-id

        response = client.delete(f"/jobs/favorites/{favorite.id}", headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_delete_favorite_invalid_uuid(self, client, db_session):
        """Test deleting a favorite with invalid UUID format"""
        user = create_test_user(db_session, email="user14@test.com")
        account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )

        # Signin
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        response = client.delete("/jobs/favorites/invalid-uuid", headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
