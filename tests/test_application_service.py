import pytest
from datetime import datetime, timezone
from uuid import uuid4, UUID

from fastapi import HTTPException, status

from app.services.application import ApplicationService
from app.dto.application import CreateApplicationDto, UpdateApplicationStatusDto
from app.domain.models.application import Application, ApplicationStatus
from app.domain.models.account import Account, AccountType


class FakeJob:
    def __init__(self, id: UUID, account_id: UUID):
        self.id = id
        self.account_id = account_id


class FakeAccount:
    def __init__(self, id: UUID, user_id: UUID, account_type: AccountType):
        self.id = id
        self.user_id = user_id
        self.account_type = account_type


class FakeApplicationRepo:
    def __init__(self):
        self._items = {}

    def create(self, application: Application) -> Application:
        self._items[application.id] = application
        return application

    def get_by_id(self, application_id: UUID):
        return self._items.get(application_id)

    def list_by_job(self, job_id: UUID, offset: int = 0, limit: int = 100):
        return [a for a in self._items.values() if a.job_id == job_id]

    def list_by_account(self, account_id: UUID, offset: int = 0, limit: int = 100):
        return [a for a in self._items.values() if a.account_id == account_id]

    def update(self, application_id: UUID, application) -> Application:
        app = self._items.get(application_id)
        if not app:
            return None
        # application may be ApplicationUpdate with attributes
        if hasattr(application, "status") and application.status is not None:
            app.status = application.status
        if hasattr(application, "message") and application.message is not None:
            app.message = application.message
        app.updated_at = datetime.now(timezone.utc)
        self._items[application_id] = app
        return app

    def delete(self, application_id: UUID) -> bool:
        if application_id in self._items:
            del self._items[application_id]
            return True
        return False


class FakeAccountRepo:
    def __init__(self, accounts):
        self._accounts = accounts

    def get_user_accounts(self, user_id, account_type=None):
        out = [a for a in self._accounts if a.user_id == user_id]
        if account_type:
            out = [a for a in out if a.account_type == account_type]
        return out


class FakeJobRepo:
    def __init__(self, jobs):
        self._jobs = {j.id: j for j in jobs}

    def read_job(self, job_id: UUID):
        return self._jobs.get(job_id)


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def droner_account(user_id):
    return FakeAccount(uuid4(), user_id, AccountType.DRONER)


@pytest.fixture
def employer_account(user_id):
    return FakeAccount(uuid4(), user_id, AccountType.EMPLOYER)


def make_service(accounts=None, jobs=None, apps=None):
    app_repo = FakeApplicationRepo()
    if apps:
        for a in apps:
            app_repo.create(a)
    acc_repo = FakeAccountRepo(accounts or [])
    job_repo = FakeJobRepo(jobs or [])
    svc = ApplicationService(app_repo, acc_repo, job_repo)
    return svc, app_repo


def make_application(job_id, account_id):
    return Application(
        id=uuid4(),
        job_id=job_id,
        account_id=account_id,
        message="hi",
        status=ApplicationStatus.PENDING,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def test_apply_job_not_found(user_id, droner_account):
    svc, _ = make_service(accounts=[droner_account], jobs=[])
    dto = CreateApplicationDto(message="please")
    with pytest.raises(HTTPException) as exc:
        svc.apply_to_job(user_id, uuid4(), dto)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


def test_apply_no_droner_account(user_id):
    svc, _ = make_service(accounts=[], jobs=[])
    dto = CreateApplicationDto(message="please")
    with pytest.raises(HTTPException) as exc:
        svc.apply_to_job(user_id, uuid4(), dto)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


def test_apply_duplicate(user_id, droner_account):
    job = FakeJob(uuid4(), uuid4())
    app = make_application(job.id, droner_account.id)
    svc, repo = make_service(accounts=[droner_account], jobs=[job], apps=[app])
    dto = CreateApplicationDto(message="again")
    with pytest.raises(HTTPException) as exc:
        svc.apply_to_job(user_id, job.id, dto)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


def test_apply_success(user_id, droner_account):
    job = FakeJob(uuid4(), uuid4())
    svc, repo = make_service(accounts=[droner_account], jobs=[job])
    dto = CreateApplicationDto(message="please")
    application = svc.apply_to_job(user_id, job.id, dto)
    assert application is not None
    assert application.job_id == job.id
    assert application.account_id == droner_account.id


def test_list_applications_for_job_not_found(user_id):
    svc, _ = make_service(accounts=[], jobs=[])
    with pytest.raises(HTTPException) as exc:
        svc.list_applications_for_job(user_id, uuid4())
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


def test_list_applications_for_job_unauthorized(user_id, droner_account):
    # job owned by someone else
    job = FakeJob(uuid4(), uuid4())
    svc, _ = make_service(accounts=[], jobs=[job])
    with pytest.raises(HTTPException) as exc:
        svc.list_applications_for_job(user_id, job.id)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN


def test_list_applications_for_job_success(user_id, employer_account):
    job = FakeJob(uuid4(), employer_account.id)
    app1 = make_application(job.id, uuid4())
    svc, _ = make_service(accounts=[employer_account], jobs=[job], apps=[app1])
    result = svc.list_applications_for_job(user_id, job.id)
    assert isinstance(result, list)
    assert len(result) == 1


def test_list_applications_for_user_no_droner(user_id):
    svc, _ = make_service(accounts=[], jobs=[])
    res = svc.list_applications_for_user(user_id)
    assert res == []


def test_update_withdraw_not_owner(user_id, droner_account):
    job = FakeJob(uuid4(), uuid4())
    app = make_application(job.id, uuid4())
    svc, repo = make_service(accounts=[droner_account], jobs=[job], apps=[app])
    dto = UpdateApplicationStatusDto(status=ApplicationStatus.WITHDRAWN)
    with pytest.raises(HTTPException) as exc:
        svc.update_application_status(user_id, app.id, dto)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN


def test_update_withdraw_success(user_id, droner_account):
    job = FakeJob(uuid4(), uuid4())
    app = make_application(job.id, droner_account.id)
    svc, repo = make_service(accounts=[droner_account], jobs=[job], apps=[app])
    dto = UpdateApplicationStatusDto(status=ApplicationStatus.WITHDRAWN)
    updated = svc.update_application_status(user_id, app.id, dto)
    assert updated.status == ApplicationStatus.WITHDRAWN


def test_update_accept_unauthorized(user_id, droner_account):
    job = FakeJob(uuid4(), uuid4())
    app = make_application(job.id, droner_account.id)
    svc, repo = make_service(accounts=[droner_account], jobs=[job], apps=[app])
    dto = UpdateApplicationStatusDto(status=ApplicationStatus.ACCEPTED)
    with pytest.raises(HTTPException) as exc:
        svc.update_application_status(user_id, app.id, dto)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN


def test_update_accept_success(user_id, employer_account):
    job = FakeJob(uuid4(), employer_account.id)
    app = make_application(job.id, uuid4())
    svc, repo = make_service(accounts=[employer_account], jobs=[job], apps=[app])
    dto = UpdateApplicationStatusDto(status=ApplicationStatus.ACCEPTED)
    updated = svc.update_application_status(user_id, app.id, dto)
    assert updated.status == ApplicationStatus.ACCEPTED


def test_delete_application_not_found(user_id):
    svc, repo = make_service(accounts=[], jobs=[])
    with pytest.raises(HTTPException) as exc:
        svc.delete_application(user_id, uuid4())
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


def test_delete_application_not_owner(user_id, droner_account):
    job = FakeJob(uuid4(), uuid4())
    app = make_application(job.id, uuid4())
    svc, repo = make_service(accounts=[droner_account], jobs=[job], apps=[app])
    with pytest.raises(HTTPException) as exc:
        svc.delete_application(user_id, app.id)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN


def test_delete_success(user_id, droner_account):
    job = FakeJob(uuid4(), uuid4())
    app = make_application(job.id, droner_account.id)
    svc, repo = make_service(accounts=[droner_account], jobs=[job], apps=[app])
    svc.delete_application(user_id, app.id)
    assert repo.get_by_id(app.id) is None
