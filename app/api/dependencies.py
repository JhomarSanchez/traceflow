from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.application.use_cases.auth import GetCurrentUser
from app.core.exceptions import TokenValidationError
from app.core.security import decode_access_token
from app.domain.entities import User
from app.domain.exceptions import AuthenticationRequiredError
from app.infrastructure.db.repositories import (
    SqlAlchemyUserRepository,
    SqlAlchemyWorkflowRepository,
)
from app.infrastructure.db.session import get_db_session

bearer_scheme = HTTPBearer(auto_error=False)


def get_user_repository(
    session: Annotated[Session, Depends(get_db_session)],
) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session)


def get_workflow_repository(
    session: Annotated[Session, Depends(get_db_session)],
) -> SqlAlchemyWorkflowRepository:
    return SqlAlchemyWorkflowRepository(session)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    user_repository: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthenticationRequiredError()

    try:
        user_id = decode_access_token(credentials.credentials)
    except TokenValidationError as exc:
        raise AuthenticationRequiredError() from exc

    use_case = GetCurrentUser(user_repository)
    return use_case(user_id=user_id)
