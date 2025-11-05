import pytest
import bcrypt
from fastapi import HTTPException

from src.services.user_service import UserService


class FakeUser:
    def __init__(self, id, email, username, password_hash):
        self.id = id
        self.email = email
        self.username = username
        self.password = password_hash
        # emulate SQLAlchemy table columns for serialization
        class Col:
            def __init__(self, name):
                self.name = name
        self.__table__ = type('T', (), {'columns': [Col('id'), Col('email'), Col('username'), Col('password')]})


class FakeUserRepo:
    def __init__(self, user=None):
        self._user = user
        self.updated = None

    def get_user_by_email(self, email):
        if self._user and self._user.email == email:
            return self._user
        return None

    def get_user_by_id(self, user_id):
        if self._user and self._user.id == user_id:
            return self._user
        return None

    def create_user(self, data):
        # return a FakeUser-like object
        u = FakeUser(1, data.get('email'), data.get('username'), data.get('password'))
        return u

    def update_user(self, user_id, data):
        self.updated = (user_id, data)
        if self._user and self._user.id == user_id:
            for k, v in data.items():
                setattr(self._user, k, v)
            return self._user
        return None

    def update(self, user):
        # pretend commit and return
        return user

    def get_all_users(self):
        return [self._user] if self._user else []


def hash_pw(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def test_authenticate_success_and_fail():
    pw = 'secret123'
    hashed = hash_pw(pw)
    user = FakeUser(42, 'u@example.com', 'user1', hashed)
    repo = FakeUserRepo(user)
    svc = UserService(user_repository=repo)

    ok = svc.authenticate('u@example.com', pw)
    assert ok is not None
    assert 'access_token' in ok
    assert ok['user']['email'] == 'u@example.com'

    bad = svc.authenticate('u@example.com', 'wrong')
    assert bad is None


def test_change_password_success_and_incorrect_current():
    old = 'oldpass'
    new = 'newpass123'
    user = FakeUser(7, 'x@x.com', 'x', hash_pw(old))
    repo = FakeUserRepo(user)
    svc = UserService(user_repository=repo)

    # incorrect current
    with pytest.raises(HTTPException):
        svc.change_password(user_id=7, current_password='nope', new_password=new)

    # correct current
    out = svc.change_password(user_id=7, current_password=old, new_password=new)
    assert out is not None
    assert repo.updated is not None
    assert repo.updated[0] == 7
    assert 'password' in repo.updated[1]
    assert repo.updated[1]['password'] != new  # should be hashed


def test_get_user_by_id_404():
    repo = FakeUserRepo(user=None)
    svc = UserService(user_repository=repo)
    with pytest.raises(HTTPException):
        svc.get_user_by_id(999)
