from __future__ import annotations

from app.domain.entities import WorkflowStep
from app.domain.enums import WorkflowStepType
from app.domain.exceptions import InvalidWorkflowDataError


def test_workflow_step_create_normalizes_supported_type_and_copies_config() -> None:
    step_config = {"message": "hello"}

    workflow_step = WorkflowStep.create(
        workflow_id="workflow-1",
        step_order=2,
        step_type="  log_message  ",
        step_config=step_config,
    )

    assert workflow_step.workflow_id == "workflow-1"
    assert workflow_step.step_order == 2
    assert workflow_step.step_type is WorkflowStepType.LOG_MESSAGE
    assert workflow_step.step_config == {"message": "hello"}
    assert workflow_step.step_config is not step_config


def test_workflow_step_create_rejects_unsupported_step_type() -> None:
    try:
        WorkflowStep.create(
            workflow_id="workflow-1",
            step_order=1,
            step_type="send_email",
            step_config={},
        )
    except InvalidWorkflowDataError as exc:
        assert exc.code == "invalid_workflow_data"
    else:
        raise AssertionError("Invalid workflow data error was expected")


def test_workflow_step_create_rejects_non_positive_step_order() -> None:
    try:
        WorkflowStep.create(
            workflow_id="workflow-1",
            step_order=0,
            step_type=WorkflowStepType.MARK_SUCCESS,
            step_config={},
        )
    except InvalidWorkflowDataError as exc:
        assert exc.code == "invalid_workflow_data"
    else:
        raise AssertionError("Invalid workflow data error was expected")


def test_workflow_step_create_rejects_non_object_step_config() -> None:
    try:
        WorkflowStep.create(
            workflow_id="workflow-1",
            step_order=1,
            step_type=WorkflowStepType.MARK_SUCCESS,
            step_config=None,  # type: ignore[arg-type]
        )
    except InvalidWorkflowDataError as exc:
        assert exc.code == "invalid_workflow_data"
    else:
        raise AssertionError("Invalid workflow data error was expected")
