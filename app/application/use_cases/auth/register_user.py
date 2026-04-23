from __future__ import annotations

from app.application.interfaces.repositories import UserRepository
from app.core.security import hash_password
from app.domain.entities import User, normalize_email
from app.domain.exceptions import EmailAlreadyExistsError


class RegisterUser:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def __call__(self, *, email: str, password: str) -> User:
        normalized_email = normalize_email(email)
        existing_user = self.user_repository.get_by_email(normalized_email)
        if existing_user is not None:
            raise EmailAlreadyExistsError()

        user = User.create(
            email=normalized_email,
            hashed_password=hash_password(password),
        )

        try:
            self.user_repository.add(user)
            self.user_repository.commit()
        except Exception:
            self.user_repository.rollback()
            raise

        return user
