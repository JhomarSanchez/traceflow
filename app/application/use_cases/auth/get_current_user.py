from __future__ import annotations

from app.application.interfaces.repositories import UserRepository
from app.domain.entities import User
from app.domain.exceptions import AuthenticationRequiredError, InactiveUserError


class GetCurrentUser:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def __call__(self, *, user_id: str) -> User:
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise AuthenticationRequiredError()
        if not user.is_active:
            raise InactiveUserError()
        return user
