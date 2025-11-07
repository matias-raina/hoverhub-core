from fastapi.testclient import TestClient

from app.main import app
from app.routers import account as account_router_module


class FakeAccountService:
    def __init__(self):
        self._store = {}

    def create_account(self, user_id, account_type_id):
        account = {
            "id": "fake-id",
            "user_id": str(user_id),
            "account_type_id": account_type_id,
            "account_status_type_id": 1,
        }
        self._store[account["id"]] = account
        return account

    def get_accounts_by_user(self, user_id):
        return [a for a in self._store.values() if a["user_id"] == str(user_id)]

    def change_account_status(self, account_id, new_status_id):
        if account_id not in self._store:
            raise ValueError("Account not found")
        self._store[account_id]["account_status_type_id"] = new_status_id
        return self._store[account_id]

    def remove_account(self, account_id):
        if account_id in self._store:
            del self._store[account_id]
            return True
        raise ValueError("Account not found")


def setup_module(module):
    # Override the dependency used by the account router to return the fake service
    app.dependency_overrides[account_router_module.get_account_service] = lambda: FakeAccountService()


def teardown_module(module):
    app.dependency_overrides.clear()


def test_create_and_list_accounts():
    client = TestClient(app)

    # create account
    resp = client.post("/accounts/?user_id=123&account_type_id=1")
    assert resp.status_code == 201
    data = resp.json()
    assert data["user_id"] == "123"
    assert data["account_type_id"] == 1

    # list accounts for user
    resp = client.get("/accounts/user/123")
    assert resp.status_code == 200
    lst = resp.json()
    assert isinstance(lst, list)
    assert any(a["user_id"] == "123" for a in lst)


def test_change_and_delete_account():
    client = TestClient(app)

    # create account
    resp = client.post("/accounts/?user_id=abc&account_type_id=2")
    assert resp.status_code == 201
    acc = resp.json()
    acc_id = acc["id"]

    # change status
    resp = client.patch(f"/accounts/{acc_id}/status?new_status_id=2")
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["account_status_type_id"] == 2

    # delete
    resp = client.delete(f"/accounts/{acc_id}")
    assert resp.status_code == 204
