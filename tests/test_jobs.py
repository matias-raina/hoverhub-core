from datetime import date, timedelta
from uuid import uuid4

from fastapi import status

from tests.utils import create_test_account, create_test_job, create_test_user, get_account_headers


class TestCreateJob:
    """Tests for POST /jobs/"""

    def test_create_job_success(self, client, db_session):
        """Test creating a job successfully"""
        # Create user and account first
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        job_data = {
            "title": "Drone Photography Job",
            "description": "Need aerial photography for real estate",
            "budget": 1500.0,
            "location": "San Francisco, CA",
            "start_date": str(date.today() + timedelta(days=7)),
            "end_date": str(date.today() + timedelta(days=14)),
        }

        response = client.post("/jobs/", json=job_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == job_data["title"]
        assert data["description"] == job_data["description"]
        assert data["budget"] == job_data["budget"]
        assert data["location"] == job_data["location"]
        assert data["account_id"] == str(account.id)
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_job_invalid_account_id(self, client, db_session):
        """Test creating a job with invalid account_id in header"""
        user = create_test_user(db_session)
        fake_account_id = uuid4()

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        # Use a non-existent account ID in header
        headers = get_account_headers(token, fake_account_id)

        job_data = {
            "title": "Test Job",
            "description": "Test description",
            "budget": 1000.0,
            "location": "Test Location",
            "start_date": str(date.today() + timedelta(days=1)),
            "end_date": str(date.today() + timedelta(days=7)),
        }

        response = client.post("/jobs/", json=job_data, headers=headers)
        # Should fail because account doesn't exist (404) or user doesn't own it (403)
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,  # Account doesn't exist
            status.HTTP_403_FORBIDDEN,  # User doesn't own the account
        ]

    def test_create_job_missing_fields(self, client, db_session):
        """Test creating a job with missing required fields"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        job_data = {
            "title": "Incomplete Job",
            # Missing required fields: description, budget, location, dates
        }

        response = client.post("/jobs/", json=job_data, headers=headers)
        # Pydantic should validate and return 422
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_job_invalid_date_range(self, client, db_session):
        """Test creating a job with end_date before start_date"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        job_data = {
            "title": "Invalid Date Job",
            "description": "Test description",
            "budget": 1000.0,
            "location": "Test Location",
            "start_date": str(date.today() + timedelta(days=7)),
            # Before start_date
            "end_date": str(date.today() + timedelta(days=1)),
        }

        response = client.post("/jobs/", json=job_data, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "End date must be on or after start date" in response.json()["detail"]

    def test_create_job_negative_budget(self, client, db_session):
        """Test creating a job with negative budget"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        job_data = {
            "title": "Negative Budget Job",
            "description": "Test description",
            "budget": -1000.0,
            "location": "Test Location",
            "start_date": str(date.today() + timedelta(days=1)),
            "end_date": str(date.today() + timedelta(days=7)),
        }

        response = client.post("/jobs/", json=job_data, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Budget must be greater than 0" in response.json()["detail"]

    def test_create_job_zero_budget(self, client, db_session):
        """Test creating a job with zero budget"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        job_data = {
            "title": "Zero Budget Job",
            "description": "Test description",
            "budget": 0.0,
            "location": "Test Location",
            "start_date": str(date.today() + timedelta(days=1)),
            "end_date": str(date.today() + timedelta(days=7)),
        }

        response = client.post("/jobs/", json=job_data, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Budget must be greater than 0" in response.json()["detail"]

    def test_create_job_past_start_date(self, client, db_session):
        """Test creating a job with start_date in the past"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        job_data = {
            "title": "Past Date Job",
            "description": "Test description",
            "budget": 1000.0,
            "location": "Test Location",
            "start_date": str(date.today() - timedelta(days=1)),  # Yesterday
            "end_date": str(date.today() + timedelta(days=7)),
        }

        response = client.post("/jobs/", json=job_data, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Date cannot be in the past" in response.json()["detail"]

    def test_create_job_past_end_date(self, client, db_session):
        """Test creating a job with end_date in the past"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        job_data = {
            "title": "Past End Date Job",
            "description": "Test description",
            "budget": 1000.0,
            "location": "Test Location",
            "start_date": str(date.today() + timedelta(days=1)),
            "end_date": str(date.today() - timedelta(days=1)),  # Yesterday
        }

        response = client.post("/jobs/", json=job_data, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Date cannot be in the past" in response.json()["detail"]

    def test_create_job_title_too_short(self, client, db_session):
        """Test creating a job with title less than 5 characters"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        job_data = {
            "title": "Job",  # Only 3 characters
            "description": "Test description",
            "budget": 1000.0,
            "location": "Test Location",
            "start_date": str(date.today() + timedelta(days=1)),
            "end_date": str(date.today() + timedelta(days=7)),
        }

        response = client.post("/jobs/", json=job_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_job_description_too_short(self, client, db_session):
        """Test creating a job with description less than 10 characters"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        job_data = {
            "title": "Valid Title",
            "description": "Short",  # Only 5 characters
            "budget": 1000.0,
            "location": "Test Location",
            "start_date": str(date.today() + timedelta(days=1)),
            "end_date": str(date.today() + timedelta(days=7)),
        }

        response = client.post("/jobs/", json=job_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_job_empty_location(self, client, db_session):
        """Test creating a job with empty location"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        job_data = {
            "title": "Valid Title",
            "description": "Valid description",
            "budget": 1000.0,
            "location": "",  # Empty string
            "start_date": str(date.today() + timedelta(days=1)),
            "end_date": str(date.today() + timedelta(days=7)),
        }

        response = client.post("/jobs/", json=job_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestGetJob:
    """Tests for GET /jobs/{job_id}"""

    def test_get_job_success(self, client, db_session):
        """Test getting a job by ID"""
        # Create job
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)
        job = create_test_job(db_session, account.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        response = client.get(f"/jobs/{job.id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(job.id)
        assert data["title"] == job.title
        assert data["description"] == job.description
        assert data["budget"] == job.budget
        assert data["account_id"] == str(job.account_id)

    def test_get_job_not_found(self, client, db_session):
        """Test getting a non-existent job returns 404"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        fake_job_id = uuid4()
        response = client.get(f"/jobs/{fake_job_id}", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_job_invalid_uuid(self, client, db_session):
        """Test getting a job with invalid UUID format"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        response = client.get("/jobs/invalid-uuid", headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_get_job_unauthorized(self, client, db_session):
        """Test getting a job from a different account returns 403"""
        # Create job with first user/account
        user1 = create_test_user(db_session, email="user1@test.com")
        account1 = create_test_account(db_session, user1.id)
        job = create_test_job(db_session, account1.id)

        # Try to access with second user/account
        user2 = create_test_user(db_session, email="user2@test.com")
        account2 = create_test_account(db_session, user2.id)

        # Signin as second user
        signin_response = client.post(
            "/auth/signin",
            json={"email": user2.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account2.id)

        response = client.get(f"/jobs/{job.id}", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestListJobs:
    """Tests for GET /jobs/"""

    def test_list_jobs_success(self, client, db_session):
        """Test listing jobs with authentication"""
        # Create multiple jobs
        user = create_test_user(db_session)
        account1 = create_test_account(db_session, user.id, name="Account 1")
        account2 = create_test_account(db_session, user.id, name="Account 2")

        create_test_job(db_session, account1.id, title="Job 1")
        create_test_job(db_session, account2.id, title="Job 2")
        create_test_job(db_session, account1.id, title="Job 3")

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account1.id)

        response = client.get("/jobs/", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

        # Verify job structure
        for job in data:
            assert "id" in job
            assert "title" in job
            assert "description" in job
            assert "budget" in job
            assert "account_id" in job

    def test_list_jobs_pagination(self, client, db_session):
        """Test listing jobs with pagination and authentication"""
        # Create multiple jobs
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Create 5 jobs
        job_ids = []
        for i in range(5):
            job = create_test_job(db_session, account.id, title=f"Job {i}")
            job_ids.append(job.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        # Test with offset and limit - first page
        response = client.get("/jobs/?offset=0&limit=2", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        # Verify ordering (newest first)
        assert data[0]["title"] == "Job 4"  # Most recent
        assert data[1]["title"] == "Job 3"

        # Test with offset - second page
        response = client.get("/jobs/?offset=2&limit=2", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        # Verify ordering continues correctly
        assert data[0]["title"] == "Job 2"
        assert data[1]["title"] == "Job 1"

        # Test with offset - third page (partial)
        response = client.get("/jobs/?offset=4&limit=2", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1  # Only one job remaining
        assert data[0]["title"] == "Job 0"

        # Test with offset beyond available items
        response = client.get("/jobs/?offset=10&limit=2", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 0  # Empty result

    def test_list_jobs_empty(self, client, db_session):
        """Test listing jobs when no jobs exist with authentication"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        response = client.get("/jobs/", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # Should be empty or contain jobs from previous tests (depending on test isolation)

    def test_list_jobs_requires_authentication(self, client, db_session):
        """Test that listing jobs requires authentication"""
        # Create jobs without authentication
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)
        create_test_job(db_session, account.id, title="Job 1")

        # Try to list jobs without authentication headers
        response = client.get("/jobs/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_jobs_invalid_account_id_header(self, client, db_session):
        """Test listing jobs with invalid account ID format in header"""
        user = create_test_user(db_session)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]

        # Use invalid UUID format in header
        headers = {
            "Authorization": f"Bearer {token}",
            "x-account-id": "invalid-uuid-format",
        }

        response = client.get("/jobs/", headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid account ID format" in response.json()["detail"]

    def test_list_jobs_missing_account_id_header(self, client, db_session):
        """Test listing jobs with missing x-account-id header"""
        user = create_test_user(db_session)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]

        # Use only Authorization header without x-account-id
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/jobs/", headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_list_jobs_pagination_validation(self, client, db_session):
        """Test pagination parameter validation"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        # Test negative offset
        response = client.get("/jobs/?offset=-1&limit=10", headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        # Test zero limit
        response = client.get("/jobs/?offset=0&limit=0", headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        # Test negative limit
        response = client.get("/jobs/?offset=0&limit=-1", headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        # Test limit exceeding maximum (100)
        response = client.get("/jobs/?offset=0&limit=101", headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        # Test valid maximum limit
        response = client.get("/jobs/?offset=0&limit=100", headers=headers)
        assert response.status_code == status.HTTP_200_OK

        # Test valid minimum limit
        response = client.get("/jobs/?offset=0&limit=1", headers=headers)
        assert response.status_code == status.HTTP_200_OK


class TestUpdateJob:
    """Tests for PUT /jobs/{job_id}"""

    def test_update_job_success(self, client, db_session):
        """Test updating a job successfully"""
        # Create job
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)
        job = create_test_job(db_session, account.id, title="Original Title")

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "budget": 2000.0,
        }

        response = client.put(f"/jobs/{job.id}", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert data["budget"] == update_data["budget"]
        assert data["id"] == str(job.id)

    def test_update_job_partial(self, client, db_session):
        """Test updating a job with partial data"""
        # Create job
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)
        job = create_test_job(db_session, account.id, title="Original Title")

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        update_data = {
            "title": "Only Title Updated",
        }

        response = client.put(f"/jobs/{job.id}", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == update_data["title"]
        # Other fields should remain unchanged
        assert data["description"] == job.description

    def test_update_job_not_found(self, client, db_session):
        """Test updating a non-existent job returns 404"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        fake_job_id = uuid4()
        update_data = {"title": "Updated Title"}

        response = client.put(f"/jobs/{fake_job_id}", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_update_job_unauthorized(self, client, db_session):
        """Test updating a job from a different account returns 403"""
        # Create job with first user/account
        user1 = create_test_user(db_session, email="user1@test.com")
        account1 = create_test_account(db_session, user1.id)
        job = create_test_job(db_session, account1.id)

        # Try to update with second user/account
        user2 = create_test_user(db_session, email="user2@test.com")
        account2 = create_test_account(db_session, user2.id)

        # Signin as second user
        signin_response = client.post(
            "/auth/signin",
            json={"email": user2.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account2.id)

        update_data = {"title": "Unauthorized Update"}
        response = client.put(f"/jobs/{job.id}", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_job_negative_budget(self, client, db_session):
        """Test updating a job with negative budget"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)
        job = create_test_job(db_session, account.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        update_data = {"budget": -500.0}

        response = client.put(f"/jobs/{job.id}", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Budget must be greater than 0" in response.json()["detail"]

    def test_update_job_zero_budget(self, client, db_session):
        """Test updating a job with zero budget"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)
        job = create_test_job(db_session, account.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        update_data = {"budget": 0.0}

        response = client.put(f"/jobs/{job.id}", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Budget must be greater than 0" in response.json()["detail"]

    def test_update_job_past_start_date(self, client, db_session):
        """Test updating a job with start_date in the past"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)
        job = create_test_job(db_session, account.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        update_data = {"start_date": str(date.today() - timedelta(days=1))}

        response = client.put(f"/jobs/{job.id}", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Date cannot be in the past" in response.json()["detail"]

    def test_update_job_past_end_date(self, client, db_session):
        """Test updating a job with end_date in the past"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)
        job = create_test_job(db_session, account.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        update_data = {"end_date": str(date.today() - timedelta(days=1))}

        response = client.put(f"/jobs/{job.id}", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Date cannot be in the past" in response.json()["detail"]

    def test_update_job_invalid_date_range(self, client, db_session):
        """Test updating a job with end_date before start_date"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)
        job = create_test_job(db_session, account.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        update_data = {
            "start_date": str(date.today() + timedelta(days=10)),
            # Before start_date
            "end_date": str(date.today() + timedelta(days=5)),
        }

        response = client.put(f"/jobs/{job.id}", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "End date must be on or after start date" in response.json()["detail"]

    def test_update_job_title_too_short(self, client, db_session):
        """Test updating a job with title less than 5 characters"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)
        job = create_test_job(db_session, account.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        update_data = {"title": "Job"}  # Only 3 characters

        response = client.put(f"/jobs/{job.id}", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_update_job_description_too_short(self, client, db_session):
        """Test updating a job with description less than 10 characters"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)
        job = create_test_job(db_session, account.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        update_data = {"description": "Short"}  # Only 5 characters

        response = client.put(f"/jobs/{job.id}", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_update_job_empty_location(self, client, db_session):
        """Test updating a job with empty location"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)
        job = create_test_job(db_session, account.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        update_data = {"location": ""}  # Empty string

        response = client.put(f"/jobs/{job.id}", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestDeleteJob:
    """Tests for DELETE /jobs/{job_id}"""

    def test_delete_job_success(self, client, db_session):
        """Test deleting a job successfully"""
        # Create job
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)
        job = create_test_job(db_session, account.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        response = client.delete(f"/jobs/{job.id}", headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify job is deleted
        get_response = client.get(f"/jobs/{job.id}", headers=headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_job_not_found(self, client, db_session):
        """Test deleting a non-existent job returns 404"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        fake_job_id = uuid4()
        response = client.delete(f"/jobs/{fake_job_id}", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_delete_job_invalid_uuid(self, client, db_session):
        """Test deleting a job with invalid UUID format"""
        user = create_test_user(db_session)
        account = create_test_account(db_session, user.id)

        # Signin to get a token
        signin_response = client.post(
            "/auth/signin",
            json={"email": user.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account.id)

        response = client.delete("/jobs/invalid-uuid", headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_delete_job_unauthorized(self, client, db_session):
        """Test deleting a job from a different account returns 403"""
        # Create job with first user/account
        user1 = create_test_user(db_session, email="user1@test.com")
        account1 = create_test_account(db_session, user1.id)
        job = create_test_job(db_session, account1.id)

        # Try to delete with second user/account
        user2 = create_test_user(db_session, email="user2@test.com")
        account2 = create_test_account(db_session, user2.id)

        # Signin as second user
        signin_response = client.post(
            "/auth/signin",
            json={"email": user2.email, "password": "testpassword123"},
        )
        token = signin_response.json()["access_token"]
        headers = get_account_headers(token, account2.id)

        response = client.delete(f"/jobs/{job.id}", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
