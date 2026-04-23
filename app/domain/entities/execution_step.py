from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from app.domain.entities.event_record import normalize_event_payload
from app.domain.enums import ExecutionStepStatus
from app.domain.exceptions import InvalidExecutionStateError


@dataclass(slots=True)
class ExecutionStep:
    id: str
    execution_id: str
    workflow_step_id: str
    status: ExecutionStepStatus
    input_data: dict[str, Any]
    output_data: dict[str, Any] | None
    error_message: str | None
    started_at: datetime
    finished_at: datetime | None

    @classmethod
    def create(
        cls,
        *,
        execution_id: str,
        workflow_step_id: str,
        input_data: Mapping[str, Any],
    ) -> "ExecutionStep":
        return cls(
            id=str(uuid4()),
            execution_id=execution_id,
            workflow_step_id=workflow_step_id,
            status=ExecutionStepStatus.PENDING,
            input_data=normalize_event_payload(input_data),
            output_data=None,
            error_message=None,
            started_at=datetime.now(UTC),
            finished_at=None,
        )

    def mark_running(self) -> None:
        if self.status is not ExecutionStepStatus.PENDING:
            raise InvalidExecutionStateError(
                "Execution step can only move to running from pending"
            )
        self.status = ExecutionStepStatus.RUNNING
        self.error_message = None

    def mark_success(self, output_data: Mapping[str, Any]) -> None:
        if self.status is not ExecutionStepStatus.RUNNING:
            raise InvalidExecutionStateError(
                "Execution step can only succeed from running"
            )
        self.status = ExecutionStepStatus.SUCCESS
        self.output_data = normalize_event_payload(output_data)
        self.finished_at = datetime.now(UTC)
        self.error_message = None

    def mark_failed(self, error_message: str) -> None:
        if self.status is not ExecutionStepStatus.RUNNING:
            raise InvalidExecutionStateError(
                "Execution step can only fail from running"
            )
        self.status = ExecutionStepStatus.FAILED
        self.finished_at = datetime.now(UTC)
        self.error_message = error_message
