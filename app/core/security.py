from __future__ import annotations

from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import Settings, get_settings
from app.core.exceptions import TokenValidationError

PASSWORD_CONTEXT = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return PASSWORD_CONTEXT.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return PASSWORD_CONTEXT.verify(password, hashed_password)


def create_access_token(
    subject: str,
    *,
    settings: Settings | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    app_settings = settings or get_settings()
    expiration_delta = expires_delta or timedelta(
        minutes=app_settings.access_token_expire_minutes
    )
    payload = {
        "sub": subject,
        "exp": datetime.now(UTC) + expiration_delta,
    }
    return jwt.encode(
        payload,
        app_settings.secret_key,
        algorithm=app_settings.jwt_algorithm,
    )


def decode_access_token(token: str, *, settings: Settings | None = None) -> str:
    app_settings = settings or get_settings()

    try:
        payload = jwt.decode(
            token,
            app_settings.secret_key,
            algorithms=[app_settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise TokenValidationError() from exc

    subject = payload.get("sub")
    if not subject or not isinstance(subject, str):
        raise TokenValidationError()

    return subject
