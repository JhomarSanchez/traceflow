from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.infrastructure.db.models.event_record import EventRecordModel
from app.infrastructure.db.models.execution import ExecutionModel
from app.infrastructure.db.models.user import UserModel
from app.infrastructure.db.models.workflow import WorkflowModel


def test_database_rejects_second_execution_for_same_event_record(db_session: Session) -> None:
    user = UserModel(
        id="user-1",
        email="owner@example.com",
        hashed_password="hashed-password",
        is_active=True,
    )
    workflow = WorkflowModel(
        id="workflow-1",
        owner_id=user.id,
        name="Workflow",
        description=None,
        event_type="user_registered",
        is_active=True,
    )
    event_record = EventRecordModel(
        id="event-1",
        workflow_id=workflow.id,
        event_type="user_registered",
        payload={"email": "user@example.com"},
        received_by_user_id=user.id,
    )
    first_execution = ExecutionModel(
        id="execution-1",
        workflow_id=workflow.id,
        event_record_id=event_record.id,
        status="success",
    )
    duplicate_execution = ExecutionModel(
        id="execution-2",
        workflow_id=workflow.id,
        event_record_id=event_record.id,
        status="failed",
    )

    db_session.add_all([user, workflow, event_record, first_execution])
    db_session.commit()

    db_session.add(duplicate_execution)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()
