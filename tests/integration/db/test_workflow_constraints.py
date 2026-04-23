from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.infrastructure.db.models.user import UserModel
from app.infrastructure.db.models.workflow import WorkflowModel


def create_user_model() -> UserModel:
    now = datetime.now(UTC)
    return UserModel(
        id=str(uuid4()),
        email=f"{uuid4()}@example.com",
        hashed_password="hashed-password",
        is_active=True,
        created_at=now,
        updated_at=now,
    )


def create_workflow_model(*, owner_id: str, event_type: str, is_active: bool) -> WorkflowModel:
    now = datetime.now(UTC)
    return WorkflowModel(
        id=str(uuid4()),
        owner_id=owner_id,
        name=f"workflow-{uuid4()}",
        description=None,
        event_type=event_type,
        is_active=is_active,
        created_at=now,
        updated_at=now,
    )


def test_database_blocks_second_active_workflow_for_same_owner_and_event_type(
    db_session: Session,
) -> None:
    user = create_user_model()
    db_session.add(user)
    db_session.commit()

    first = create_workflow_model(
        owner_id=user.id,
        event_type="user_registered",
        is_active=True,
    )
    second = create_workflow_model(
        owner_id=user.id,
        event_type="user_registered",
        is_active=True,
    )
    db_session.add(first)
    db_session.commit()

    db_session.add(second)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_database_allows_inactive_duplicate_event_type_for_same_owner(
    db_session: Session,
) -> None:
    user = create_user_model()
    db_session.add(user)
    db_session.commit()

    active_workflow = create_workflow_model(
        owner_id=user.id,
        event_type="user_registered",
        is_active=True,
    )
    inactive_workflow = create_workflow_model(
        owner_id=user.id,
        event_type="user_registered",
        is_active=False,
    )

    db_session.add(active_workflow)
    db_session.commit()
    db_session.add(inactive_workflow)
    db_session.commit()
