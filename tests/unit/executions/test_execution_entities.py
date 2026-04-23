from __future__ import annotations

from app.domain.entities import Execution, ExecutionStep
from app.domain.enums import ExecutionStatus, ExecutionStepStatus
from app.domain.exceptions import InvalidExecutionStateError


def test_execution_lifecycle_reaches_success_terminal_state() -> None:
    execution = Execution.create(
        workflow_id="workflow-1",
        event_record_id="event-1",
    )

    execution.mark_running()
    execution.mark_success()

    assert execution.status is ExecutionStatus.SUCCESS
    assert execution.finished_at is not None
    assert execution.error_message is None


def test_execution_rejects_invalid_success_transition() -> None:
    execution = Execution.create(
        workflow_id="workflow-1",
        event_record_id="event-1",
    )

    try:
        execution.mark_success()
    except InvalidExecutionStateError as exc:
        assert exc.code == "invalid_execution_state"
    else:
        raise AssertionError("Invalid execution state error was expected")


def test_execution_step_failure_records_terminal_state() -> None:
    execution_step = ExecutionStep.create(
        execution_id="execution-1",
        workflow_step_id="workflow-step-1",
        input_data={"email": "user@example.com"},
    )

    execution_step.mark_running()
    execution_step.mark_failed("step failed")

    assert execution_step.status is ExecutionStepStatus.FAILED
    assert execution_step.finished_at is not None
    assert execution_step.error_message == "step failed"


def test_execution_step_rejects_failure_before_running() -> None:
    execution_step = ExecutionStep.create(
        execution_id="execution-1",
        workflow_step_id="workflow-step-1",
        input_data={"email": "user@example.com"},
    )

    try:
        execution_step.mark_failed("step failed")
    except InvalidExecutionStateError as exc:
        assert exc.code == "invalid_execution_state"
    else:
        raise AssertionError("Invalid execution state error was expected")
