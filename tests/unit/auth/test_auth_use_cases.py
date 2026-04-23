from __future__ import annotations

from app.application.use_cases.auth import LoginUser, RegisterUser
from app.core.security import verify_password
from app.domain.entities import User
from app.domain.exceptions import InvalidCredentialsError


class FakeUserRepository:
    def __init__(self) -> None:
        self.users_by_id: dict[str, User] = {}
        self.users_by_email: dict[str, User] = {}

    def get_by_email(self, email: str) -> User | None:
        return self.users_by_email.get(email)

    def get_by_id(self, user_id: str) -> User | None:
        return self.users_by_id.get(user_id)

    def add(self, user: User) -> User:
        self.users_by_id[user.id] = user
        self.users_by_email[user.email] = user
        return user

    def commit(self) -> None:
        return None

    def rollback(self) -> None:
        return None


def test_register_user_normalizes_email_and_hashes_password() -> None:
    repository = FakeUserRepository()

    use_case = RegisterUser(repository)
    user = use_case(email="  USER@Example.com  ", password="StrongPass123")

    assert user.email == "user@example.com"
    assert user.hashed_password != "StrongPass123"
    assert verify_password("StrongPass123", user.hashed_password) is True


def test_login_user_rejects_invalid_password() -> None:
    repository = FakeUserRepository()
    user = RegisterUser(repository)(email="user@example.com", password="StrongPass123")

    use_case = LoginUser(repository)

    try:
        use_case(email=user.email, password="wrong-pass")
    except InvalidCredentialsError as exc:
        assert exc.code == "invalid_credentials"
    else:
        raise AssertionError("Invalid credentials error was expected")
