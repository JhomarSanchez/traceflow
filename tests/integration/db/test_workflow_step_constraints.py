from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.infrastructure.db.models.user import UserModel
from app.infrastructure.db.models.workflow import WorkflowModel
from app.infrastructure.db.models.workflow_step import WorkflowStepModel


def test_database_rejects_duplicate_step_order_in_same_workflow(db_session: Session) -> None:
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
    first_step = WorkflowStepModel(
        id="step-1",
        workflow_id=workflow.id,
        step_order=1,
        step_type="log_message",
        step_config={"message": "hello"},
    )
    duplicate_step = WorkflowStepModel(
        id="step-2",
        workflow_id=workflow.id,
        step_order=1,
        step_type="mark_success",
        step_config={},
    )

    db_session.add_all([user, workflow, first_step])
    db_session.commit()

    db_session.add(duplicate_step)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_database_allows_same_step_order_across_different_workflows(db_session: Session) -> None:
    user = UserModel(
        id="user-1",
        email="owner@example.com",
        hashed_password="hashed-password",
        is_active=True,
    )
    first_workflow = WorkflowModel(
        id="workflow-1",
        owner_id=user.id,
        name="Workflow 1",
        description=None,
        event_type="user_registered",
        is_active=True,
    )
    second_workflow = WorkflowModel(
        id="workflow-2",
        owner_id=user.id,
        name="Workflow 2",
        description=None,
        event_type="order_created",
        is_active=True,
    )
    first_step = WorkflowStepModel(
        id="step-1",
        workflow_id=first_workflow.id,
        step_order=1,
        step_type="log_message",
        step_config={"message": "hello"},
    )
    second_step = WorkflowStepModel(
        id="step-2",
        workflow_id=second_workflow.id,
        step_order=1,
        step_type="mark_success",
        step_config={},
    )

    db_session.add_all([user, first_workflow, second_workflow, first_step, second_step])
    db_session.commit()

    persisted_steps = db_session.scalars(
        select(WorkflowStepModel).order_by(WorkflowStepModel.id.asc())
    ).all()

    assert [step.id for step in persisted_steps] == ["step-1", "step-2"]
