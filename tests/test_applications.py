from uuid import uuid4

from fastapi import status

from app.domain.models.account import AccountType
from app.domain.models.application import ApplicationStatus
from tests.utils import (
    create_test_account,
    create_test_application,
    create_test_job,
    create_test_user,
    get_auth_headers,
)


class TestApplyToJob:
    """Tests for POST /applications/jobs/{job_id}"""

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
        headers = get_auth_headers(token)

        application_data = {"message": "I'm interested in this job!"}

        response = client.post(
            f"/applications/jobs/{job.id}", json=application_data, headers=headers
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
        headers = get_auth_headers(token)

        application_data = {}  # No message

        response = client.post(
            f"/applications/jobs/{job.id}", json=application_data, headers=headers
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

        # Create user without droner account
        user = create_test_user(db_session, email="user@test.com")

        # Signin
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        application_data = {"message": "I want to apply"}

        response = client.post(
            f"/applications/jobs/{job.id}", json=application_data, headers=headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "no droner account" in response.json()["detail"].lower()

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
        headers = get_auth_headers(token)

        application_data = {"message": "I want to apply again"}

        response = client.post(
            f"/applications/jobs/{job.id}", json=application_data, headers=headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()

    def test_apply_to_job_not_found(self, client, db_session):
        """Test applying to a non-existent job"""
        # Create droner user and account
        droner_user = create_test_user(db_session, email="droner5@test.com")
        create_test_account(db_session, droner_user.id, account_type=AccountType.DRONER)

        # Signin as droner
        signin_response = client.post(
            "/auth/signin",
            json={"email": droner_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        fake_job_id = uuid4()
        application_data = {"message": "I want to apply"}

        response = client.post(
            f"/applications/jobs/{fake_job_id}", json=application_data, headers=headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_apply_to_job_unauthenticated(self, client):
        """Test applying to a job without authentication"""
        fake_job_id = uuid4()
        application_data = {"message": "I want to apply"}

        response = client.post(f"/applications/jobs/{fake_job_id}", json=application_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestListApplicationsForJob:
    """Tests for GET /applications/jobs/{job_id}"""

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
        headers = get_auth_headers(token)

        response = client.get(f"/applications/jobs/{job.id}", headers=headers)
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
        create_test_account(db_session, other_employer_user.id, account_type=AccountType.EMPLOYER)

        # Signin as other employer
        signin_response = client.post(
            "/auth/signin",
            json={"email": other_employer_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        response = client.get(f"/applications/jobs/{job.id}", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "not authorized" in response.json()["detail"].lower()

    def test_list_applications_for_job_not_found(self, client, db_session):
        """Test listing applications for a non-existent job"""
        employer_user = create_test_user(db_session, email="employer9@test.com")
        create_test_account(db_session, employer_user.id, account_type=AccountType.EMPLOYER)

        # Signin as employer
        signin_response = client.post(
            "/auth/signin",
            json={"email": employer_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        fake_job_id = uuid4()
        response = client.get(f"/applications/jobs/{fake_job_id}", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_applications_for_job_unauthenticated(self, client):
        """Test listing applications without authentication"""
        fake_job_id = uuid4()
        response = client.get(f"/applications/jobs/{fake_job_id}")
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
        headers = get_auth_headers(token)

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
        # User has no accounts

        # Signin
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        response = client.get("/applications/", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0  # Empty list

    def test_list_applications_for_user_unauthenticated(self, client):
        """Test listing applications without authentication"""
        response = client.get("/applications/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUpdateApplicationStatus:
    """Tests for PATCH /applications/{application_id}"""

    def test_update_application_status_withdraw(self, client, db_session):
        """Test withdrawing an application (by droner)"""
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
        headers = get_auth_headers(token)

        update_data = {"status": ApplicationStatus.WITHDRAWN.value}

        response = client.patch(
            f"/applications/{application.id}", json=update_data, headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == ApplicationStatus.WITHDRAWN.value
        assert data["id"] == str(application.id)

    def test_update_application_status_accept(self, client, db_session):
        """Test accepting an application (by employer)"""
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
        headers = get_auth_headers(token)

        update_data = {"status": ApplicationStatus.ACCEPTED.value}

        response = client.patch(
            f"/applications/{application.id}", json=update_data, headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == ApplicationStatus.ACCEPTED.value

    def test_update_application_status_reject(self, client, db_session):
        """Test rejecting an application (by employer)"""
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

        # Signin as employer
        signin_response = client.post(
            "/auth/signin",
            json={"email": employer_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        update_data = {"status": ApplicationStatus.REJECTED.value}

        response = client.patch(
            f"/applications/{application.id}", json=update_data, headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == ApplicationStatus.REJECTED.value

    def test_update_application_status_unauthorized_withdraw(self, client, db_session):
        """Test withdrawing someone else's application (should fail)"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer14@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create two droner users
        droner_user1 = create_test_user(db_session, email="droner14a@test.com")
        droner_account1 = create_test_account(
            db_session, droner_user1.id, account_type=AccountType.DRONER
        )
        droner_user2 = create_test_user(db_session, email="droner14b@test.com")
        create_test_account(db_session, droner_user2.id, account_type=AccountType.DRONER)

        application = create_test_application(db_session, job.id, droner_account1.id)

        # Signin as droner2 (different from the one who applied)
        signin_response = client.post(
            "/auth/signin",
            json={"email": droner_user2.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        update_data = {"status": ApplicationStatus.WITHDRAWN.value}

        response = client.patch(
            f"/applications/{application.id}", json=update_data, headers=headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "not allowed" in response.json()["detail"].lower()

    def test_update_application_status_unauthorized_accept(self, client, db_session):
        """Test accepting an application for a job you don't own (should fail)"""
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

        # Create another employer
        other_employer_user = create_test_user(db_session, email="employer16@test.com")
        create_test_account(db_session, other_employer_user.id, account_type=AccountType.EMPLOYER)

        # Signin as other employer
        signin_response = client.post(
            "/auth/signin",
            json={"email": other_employer_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        update_data = {"status": ApplicationStatus.ACCEPTED.value}

        response = client.patch(
            f"/applications/{application.id}", json=update_data, headers=headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "not allowed" in response.json()["detail"].lower()

    def test_update_application_status_not_found(self, client, db_session):
        """Test updating a non-existent application"""
        droner_user = create_test_user(db_session, email="droner16@test.com")
        create_test_account(db_session, droner_user.id, account_type=AccountType.DRONER)

        # Signin
        signin_response = client.post(
            "/auth/signin",
            json={"email": droner_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        fake_application_id = uuid4()
        update_data = {"status": ApplicationStatus.WITHDRAWN.value}

        response = client.patch(
            f"/applications/{fake_application_id}", json=update_data, headers=headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_application_status_unauthenticated(self, client):
        """Test updating application status without authentication"""
        fake_application_id = uuid4()
        update_data = {"status": ApplicationStatus.ACCEPTED.value}

        response = client.patch(f"/applications/{fake_application_id}", json=update_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDeleteApplication:
    """Tests for DELETE /applications/{application_id}"""

    def test_delete_application_success(self, client, db_session):
        """Test deleting an application successfully"""
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

        # Signin as droner
        signin_response = client.post(
            "/auth/signin",
            json={"email": droner_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        response = client.delete(f"/applications/{application.id}", headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify application is deleted
        get_response = client.get("/applications/", headers=headers)
        assert get_response.status_code == status.HTTP_200_OK
        data = get_response.json()
        app_ids = [app["id"] for app in data]
        assert str(application.id) not in app_ids

    def test_delete_application_unauthorized(self, client, db_session):
        """Test deleting someone else's application (should fail)"""
        # Create employer user and account
        employer_user = create_test_user(db_session, email="employer18@test.com")
        employer_account = create_test_account(
            db_session, employer_user.id, account_type=AccountType.EMPLOYER
        )
        job = create_test_job(db_session, employer_account.id)

        # Create two droner users
        droner_user1 = create_test_user(db_session, email="droner18a@test.com")
        droner_account1 = create_test_account(
            db_session, droner_user1.id, account_type=AccountType.DRONER
        )
        droner_user2 = create_test_user(db_session, email="droner18b@test.com")
        create_test_account(db_session, droner_user2.id, account_type=AccountType.DRONER)

        application = create_test_application(db_session, job.id, droner_account1.id)

        # Signin as droner2 (different from the one who applied)
        signin_response = client.post(
            "/auth/signin",
            json={"email": droner_user2.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        response = client.delete(f"/applications/{application.id}", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "not allowed" in response.json()["detail"].lower()

    def test_delete_application_not_found(self, client, db_session):
        """Test deleting a non-existent application"""
        droner_user = create_test_user(db_session, email="droner19@test.com")
        create_test_account(db_session, droner_user.id, account_type=AccountType.DRONER)

        # Signin
        signin_response = client.post(
            "/auth/signin",
            json={"email": droner_user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_auth_headers(token)

        fake_application_id = uuid4()
        response = client.delete(f"/applications/{fake_application_id}", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_application_unauthenticated(self, client):
        """Test deleting an application without authentication"""
        fake_application_id = uuid4()
        response = client.delete(f"/applications/{fake_application_id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN
