from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4


def normalize_email(email: str) -> str:
    return email.strip().lower()


@dataclass(slots=True)
class User:
    id: str
    email: str
    hashed_password: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, *, email: str, hashed_password: str) -> "User":
        now = datetime.now(UTC)
        return cls(
            id=str(uuid4()),
            email=normalize_email(email),
            hashed_password=hashed_password,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
