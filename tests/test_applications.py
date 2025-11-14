from uuid import uuid4

from fastapi import status

from app.domain.models.account import AccountType
from app.domain.models.application import ApplicationStatus
from tests.utils import (
    create_test_account,
    create_test_application,
    create_test_job,
    create_test_user,
    get_account_headers,
)


class TestApplyToJob:
    """Tests for POST /jobs/{job_id}/applications"""

    def test_apply_to_job_success(self, client, db_session):
        """Test applying to a job successfully"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer@test.com")
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

        application_data = {"message": "I'm interested in this job!"}

        response = client.post(
            f"/jobs/{job.id}/applications", json=application_data, headers=headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["job_id"] == str(job.id)
        assert data["account_id"] == str(droner_account.id)
        assert data["status"] == ApplicationStatus.PENDING.value
        assert data["message"] == application_data["message"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_apply_to_job_without_message(self, client, db_session):
        """Test applying to a job without a message"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer2@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create droner user and account
        droner_user = create_test_user(db_session, email="droner2@test.com")
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

        application_data: dict[str, str] = {}  # No message

        response = client.post(
            f"/jobs/{job.id}/applications", json=application_data, headers=headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["job_id"] == str(job.id)
        assert data["account_id"] == str(droner_account.id)
        assert data["status"] == ApplicationStatus.PENDING.value

    def test_apply_to_job_no_droner_account(self, client, db_session):
        """Test applying to a job without a droner account"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer3@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create user with employer account (not droner)
        user = create_test_user(db_session, email="user@test.com")
        employer_account_user = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )

        # Signin
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, employer_account_user.id)

        application_data = {"message": "I want to apply"}

        response = client.post(
            f"/jobs/{job.id}/applications", json=application_data, headers=headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "droner account" in response.json()["detail"].lower()

    def test_apply_to_job_duplicate(self, client, db_session):
        """Test applying to the same job twice (should fail)"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer4@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create droner user and account
        droner_user = create_test_user(db_session, email="droner4@test.com")
        droner_account = create_test_account(
            db_session, droner_user.id, account_type=AccountType.DRONER
        )

        # Create existing application
        create_test_application(db_session, job.id, droner_account.id)

        # Signin as droner
        signin_response = client.post(
            "/auth/signin",
            json={"email": droner_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, droner_account.id)

        application_data = {"message": "I want to apply again"}

        response = client.post(
            f"/jobs/{job.id}/applications", json=application_data, headers=headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()

    def test_apply_to_job_not_found(self, client, db_session):
        """Test applying to a non-existent job"""
        # Create droner user and account
        droner_user = create_test_user(db_session, email="droner5@test.com")
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

        fake_job_id = uuid4()
        application_data = {"message": "I want to apply"}

        response = client.post(
            f"/jobs/{fake_job_id}/applications", json=application_data, headers=headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_apply_to_job_unauthenticated(self, client):
        """Test applying to a job without authentication"""
        fake_job_id = uuid4()
        application_data = {"message": "I want to apply"}

        response = client.post(f"/jobs/{fake_job_id}/applications", json=application_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestListApplicationsForJob:
    """Tests for GET /jobs/{job_id}/applications"""

    def test_list_applications_for_job_success(self, client, db_session):
        """Test listing applications for a job (as employer)"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer6@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create droner accounts and applications
        droner_user1 = create_test_user(db_session, email="droner6a@test.com")
        droner_account1 = create_test_account(
            db_session, droner_user1.id, account_type=AccountType.DRONER
        )
        droner_user2 = create_test_user(db_session, email="droner6b@test.com")
        droner_account2 = create_test_account(
            db_session, droner_user2.id, account_type=AccountType.DRONER
        )

        app1 = create_test_application(db_session, job.id, droner_account1.id)
        app2 = create_test_application(db_session, job.id, droner_account2.id)

        # Signin as employer
        signin_response = client.post(
            "/auth/signin",
            json={"email": employer_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, employer_account.id)

        response = client.get(f"/jobs/{job.id}/applications", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

        app_ids = [app["id"] for app in data]
        assert str(app1.id) in app_ids
        assert str(app2.id) in app_ids

    def test_list_applications_for_job_unauthorized(self, client, db_session):
        """Test listing applications for a job you don't own"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer7@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create another employer user
        other_employer_user = create_test_user(db_session, email="employer8@test.com")
        other_employer_account = create_test_account(
            db_session, other_employer_user.id, account_type=AccountType.EMPLOYER
        )

        # Signin as other employer
        signin_response = client.post(
            "/auth/signin",
            json={"email": other_employer_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, other_employer_account.id)

        response = client.get(f"/jobs/{job.id}/applications", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "not authorized" in response.json()["detail"].lower()

    def test_list_applications_for_job_not_found(self, client, db_session):
        """Test listing applications for a non-existent job"""
        employer_user = create_test_user(db_session, email="employer9@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )

        # Signin as employer
        signin_response = client.post(
            "/auth/signin",
            json={"email": employer_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, employer_account.id)

        fake_job_id = uuid4()
        response = client.get(f"/jobs/{fake_job_id}/applications", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_applications_for_job_unauthenticated(self, client):
        """Test listing applications without authentication"""
        fake_job_id = uuid4()
        response = client.get(f"/jobs/{fake_job_id}/applications")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestListApplicationsForUser:
    """Tests for GET /applications/"""

    def test_list_applications_for_user_success(self, client, db_session):
        """Test listing applications for the authenticated user"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer10@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job1 = create_test_job(db_session, employer_account.id)
        job2 = create_test_job(db_session, employer_account.id)

        # Create droner user and account
        droner_user = create_test_user(db_session, email="droner10@test.com")
        droner_account = create_test_account(
            db_session, droner_user.id, account_type=AccountType.DRONER
        )

        # Create applications
        app1 = create_test_application(db_session, job1.id, droner_account.id)
        app2 = create_test_application(db_session, job2.id, droner_account.id)

        # Signin as droner
        signin_response = client.post(
            "/auth/signin",
            json={"email": droner_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, droner_account.id)

        response = client.get("/applications/", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

        app_ids = [app["id"] for app in data]
        assert str(app1.id) in app_ids
        assert str(app2.id) in app_ids

    def test_list_applications_for_user_no_droner_account(self, client, db_session):
        """Test listing applications when user has no droner account"""
        user = create_test_user(db_session, email="user10@test.com")
        # User has no accounts - this will fail because x-account-id header is required
        # So we create an employer account to test the authorization check
        employer_account = create_test_account(
            db_session, user.id, account_type=AccountType.EMPLOYER
        )

        # Signin
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, employer_account.id)

        response = client.get("/applications/", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "not authorized" in response.json()["detail"].lower()

    def test_list_applications_for_user_unauthenticated(self, client):
        """Test listing applications without authentication"""
        response = client.get("/applications/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetApplication:
    """Tests for GET /applications/{application_id}"""

    def test_get_application_as_droner_owner(self, client, db_session):
        """Test getting an application as the droner who submitted it"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer11@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create droner user and account
        droner_user = create_test_user(db_session, email="droner11@test.com")
        droner_account = create_test_account(
            db_session, droner_user.id, account_type=AccountType.DRONER
        )

        application = create_test_application(db_session, job.id, droner_account.id)

        # Signin as droner
        signin_response = client.post(
            "/auth/signin",
            json={"email": droner_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, droner_account.id)

        response = client.get(f"/applications/{application.id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(application.id)
        assert data["job_id"] == str(job.id)
        assert data["account_id"] == str(droner_account.id)
        assert data["status"] == ApplicationStatus.PENDING.value

    def test_get_application_as_job_owner(self, client, db_session):
        """Test getting an application as the employer who owns the job"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer12@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create droner user and account
        droner_user = create_test_user(db_session, email="droner12@test.com")
        droner_account = create_test_account(
            db_session, droner_user.id, account_type=AccountType.DRONER
        )

        application = create_test_application(db_session, job.id, droner_account.id)

        # Signin as employer
        signin_response = client.post(
            "/auth/signin",
            json={"email": employer_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, employer_account.id)

        response = client.get(f"/applications/{application.id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(application.id)
        assert data["job_id"] == str(job.id)

    def test_get_application_unauthorized(self, client, db_session):
        """Test getting an application you don't have access to"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer13@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create droner user and account
        droner_user = create_test_user(db_session, email="droner13@test.com")
        droner_account = create_test_account(
            db_session, droner_user.id, account_type=AccountType.DRONER
        )

        application = create_test_application(db_session, job.id, droner_account.id)

        # Create another droner
        other_droner_user = create_test_user(db_session, email="droner13b@test.com")
        other_droner_account = create_test_account(
            db_session, other_droner_user.id, account_type=AccountType.DRONER
        )

        # Signin as other droner
        signin_response = client.post(
            "/auth/signin",
            json={"email": other_droner_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, other_droner_account.id)

        response = client.get(f"/applications/{application.id}", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "not authorized" in response.json()["detail"].lower()

    def test_get_application_not_found(self, client, db_session):
        """Test getting a non-existent application"""
        droner_user = create_test_user(db_session, email="droner14@test.com")
        droner_account = create_test_account(
            db_session, droner_user.id, account_type=AccountType.DRONER
        )

        # Signin
        signin_response = client.post(
            "/auth/signin",
            json={"email": droner_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, droner_account.id)

        fake_application_id = uuid4()
        response = client.get(f"/applications/{fake_application_id}", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_application_unauthenticated(self, client):
        """Test getting an application without authentication"""
        fake_application_id = uuid4()
        response = client.get(f"/applications/{fake_application_id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestWithdrawApplication:
    """Tests for POST /applications/{application_id}/withdraw"""

    def test_withdraw_application_success(self, client, db_session):
        """Test withdrawing an application successfully"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer15@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create droner user and account
        droner_user = create_test_user(db_session, email="droner15@test.com")
        droner_account = create_test_account(
            db_session, droner_user.id, account_type=AccountType.DRONER
        )

        application = create_test_application(db_session, job.id, droner_account.id)

        # Signin as droner
        signin_response = client.post(
            "/auth/signin",
            json={"email": droner_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, droner_account.id)

        response = client.post(f"/applications/{application.id}/withdraw", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == ApplicationStatus.WITHDRAWN.value
        assert data["id"] == str(application.id)

    def test_withdraw_application_unauthorized(self, client, db_session):
        """Test withdrawing someone else's application (should fail)"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer16@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create two droner users
        droner_user1 = create_test_user(db_session, email="droner16a@test.com")
        droner_account1 = create_test_account(
            db_session, droner_user1.id, account_type=AccountType.DRONER
        )
        droner_user2 = create_test_user(db_session, email="droner16b@test.com")
        droner_account2 = create_test_account(
            db_session, droner_user2.id, account_type=AccountType.DRONER
        )

        application = create_test_application(db_session, job.id, droner_account1.id)

        # Signin as droner2 (different from the one who applied)
        signin_response = client.post(
            "/auth/signin",
            json={"email": droner_user2.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, droner_account2.id)

        response = client.post(f"/applications/{application.id}/withdraw", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "not authorized" in response.json()["detail"].lower()

    def test_withdraw_application_not_droner(self, client, db_session):
        """Test withdrawing an application as employer (should fail)"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer17@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create droner user and account
        droner_user = create_test_user(db_session, email="droner17@test.com")
        droner_account = create_test_account(
            db_session, droner_user.id, account_type=AccountType.DRONER
        )

        application = create_test_application(db_session, job.id, droner_account.id)

        # Signin as employer
        signin_response = client.post(
            "/auth/signin",
            json={"email": employer_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, employer_account.id)

        response = client.post(f"/applications/{application.id}/withdraw", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "droner" in response.json()["detail"].lower()

    def test_withdraw_application_not_found(self, client, db_session):
        """Test withdrawing a non-existent application"""
        droner_user = create_test_user(db_session, email="droner18@test.com")
        droner_account = create_test_account(
            db_session, droner_user.id, account_type=AccountType.DRONER
        )

        # Signin
        signin_response = client.post(
            "/auth/signin",
            json={"email": droner_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, droner_account.id)

        fake_application_id = uuid4()
        response = client.post(f"/applications/{fake_application_id}/withdraw", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_withdraw_application_unauthenticated(self, client):
        """Test withdrawing an application without authentication"""
        fake_application_id = uuid4()
        response = client.post(f"/applications/{fake_application_id}/withdraw")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAcceptApplication:
    """Tests for POST /applications/{application_id}/accept"""

    def test_accept_application_success(self, client, db_session):
        """Test accepting an application successfully"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer19@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create droner user and account
        droner_user = create_test_user(db_session, email="droner19@test.com")
        droner_account = create_test_account(
            db_session, droner_user.id, account_type=AccountType.DRONER
        )

        application = create_test_application(db_session, job.id, droner_account.id)

        # Signin as employer
        signin_response = client.post(
            "/auth/signin",
            json={"email": employer_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, employer_account.id)

        response = client.post(f"/applications/{application.id}/accept", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == ApplicationStatus.ACCEPTED.value
        assert data["id"] == str(application.id)

    def test_accept_application_unauthorized(self, client, db_session):
        """Test accepting an application for a job you don't own (should fail)"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer20@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create droner user and account
        droner_user = create_test_user(db_session, email="droner20@test.com")
        droner_account = create_test_account(
            db_session, droner_user.id, account_type=AccountType.DRONER
        )

        application = create_test_application(db_session, job.id, droner_account.id)

        # Create another employer
        other_employer_user = create_test_user(db_session, email="employer21@test.com")
        other_employer_account = create_test_account(
            db_session, other_employer_user.id, account_type=AccountType.EMPLOYER
        )

        # Signin as other employer
        signin_response = client.post(
            "/auth/signin",
            json={"email": other_employer_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, other_employer_account.id)

        response = client.post(f"/applications/{application.id}/accept", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "not authorized" in response.json()["detail"].lower()

    def test_accept_application_not_employer(self, client, db_session):
        """Test accepting an application as droner (should fail)"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer22@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create droner user and account
        droner_user = create_test_user(db_session, email="droner22@test.com")
        droner_account = create_test_account(
            db_session, droner_user.id, account_type=AccountType.DRONER
        )

        application = create_test_application(db_session, job.id, droner_account.id)

        # Signin as droner
        signin_response = client.post(
            "/auth/signin",
            json={"email": droner_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, droner_account.id)

        response = client.post(f"/applications/{application.id}/accept", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "employer" in response.json()["detail"].lower()

    def test_accept_application_not_found(self, client, db_session):
        """Test accepting a non-existent application"""
        employer_user = create_test_user(db_session, email="employer23@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )

        # Signin
        signin_response = client.post(
            "/auth/signin",
            json={"email": employer_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, employer_account.id)

        fake_application_id = uuid4()
        response = client.post(f"/applications/{fake_application_id}/accept", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_accept_application_unauthenticated(self, client):
        """Test accepting an application without authentication"""
        fake_application_id = uuid4()
        response = client.post(f"/applications/{fake_application_id}/accept")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestRejectApplication:
    """Tests for POST /applications/{application_id}/reject"""

    def test_reject_application_success(self, client, db_session):
        """Test rejecting an application successfully"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer24@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create droner user and account
        droner_user = create_test_user(db_session, email="droner24@test.com")
        droner_account = create_test_account(
            db_session, droner_user.id, account_type=AccountType.DRONER
        )

        application = create_test_application(db_session, job.id, droner_account.id)

        # Signin as employer
        signin_response = client.post(
            "/auth/signin",
            json={"email": employer_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, employer_account.id)

        response = client.post(f"/applications/{application.id}/reject", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == ApplicationStatus.REJECTED.value
        assert data["id"] == str(application.id)

    def test_reject_application_unauthorized(self, client, db_session):
        """Test rejecting an application for a job you don't own (should fail)"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer25@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create droner user and account
        droner_user = create_test_user(db_session, email="droner25@test.com")
        droner_account = create_test_account(
            db_session, droner_user.id, account_type=AccountType.DRONER
        )

        application = create_test_application(db_session, job.id, droner_account.id)

        # Create another employer
        other_employer_user = create_test_user(db_session, email="employer26@test.com")
        other_employer_account = create_test_account(
            db_session, other_employer_user.id, account_type=AccountType.EMPLOYER
        )

        # Signin as other employer
        signin_response = client.post(
            "/auth/signin",
            json={"email": other_employer_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, other_employer_account.id)

        response = client.post(f"/applications/{application.id}/reject", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "not authorized" in response.json()["detail"].lower()

    def test_reject_application_not_employer(self, client, db_session):
        """Test rejecting an application as droner (should fail)"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer27@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create droner user and account
        droner_user = create_test_user(db_session, email="droner27@test.com")
        droner_account = create_test_account(
            db_session, droner_user.id, account_type=AccountType.DRONER
        )

        application = create_test_application(db_session, job.id, droner_account.id)

        # Signin as droner
        signin_response = client.post(
            "/auth/signin",
            json={"email": droner_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, droner_account.id)

        response = client.post(f"/applications/{application.id}/reject", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "employer" in response.json()["detail"].lower()

    def test_reject_application_not_found(self, client, db_session):
        """Test rejecting a non-existent application"""
        employer_user = create_test_user(db_session, email="employer28@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )

        # Signin
        signin_response = client.post(
            "/auth/signin",
            json={"email": employer_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, employer_account.id)

        fake_application_id = uuid4()
        response = client.post(f"/applications/{fake_application_id}/reject", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_reject_application_unauthenticated(self, client):
        """Test rejecting an application without authentication"""
        fake_application_id = uuid4()
        response = client.post(f"/applications/{fake_application_id}/reject")
        assert response.status_code == status.HTTP_403_FORBIDDEN
