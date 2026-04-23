from __future__ import annotations

from app.domain.entities import Workflow
from app.domain.exceptions import InvalidWorkflowDataError


def test_workflow_create_normalizes_fields_and_is_active_by_default() -> None:
    workflow = Workflow.create(
        owner_id="user-1",
        name="  User Registration Workflow  ",
        description="  Handles new users  ",
        event_type="  user_registered  ",
    )

    assert workflow.owner_id == "user-1"
    assert workflow.name == "User Registration Workflow"
    assert workflow.description == "Handles new users"
    assert workflow.event_type == "user_registered"
    assert workflow.is_active is True


def test_workflow_create_rejects_empty_name() -> None:
    try:
        Workflow.create(
            owner_id="user-1",
            name="   ",
            description=None,
            event_type="user_registered",
        )
    except InvalidWorkflowDataError as exc:
        assert exc.code == "invalid_workflow_data"
    else:
        raise AssertionError("Invalid workflow data error was expected")
