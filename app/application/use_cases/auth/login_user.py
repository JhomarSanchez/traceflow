from __future__ import annotations

from app.application.interfaces.repositories import UserRepository
from app.core.security import create_access_token, verify_password
from app.domain.entities import normalize_email
from app.domain.exceptions import InvalidCredentialsError


class LoginUser:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def __call__(self, *, email: str, password: str) -> str:
        normalized_email = normalize_email(email)
        user = self.user_repository.get_by_email(normalized_email)

        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        return create_access_token(user.id)
