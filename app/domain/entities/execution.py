from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from app.domain.enums import ExecutionStatus
from app.domain.exceptions import InvalidExecutionStateError


@dataclass(slots=True)
class Execution:
    id: str
    workflow_id: str
    event_record_id: str
    status: ExecutionStatus
    started_at: datetime
    finished_at: datetime | None
    error_message: str | None

    @classmethod
    def create(
        cls,
        *,
        workflow_id: str,
        event_record_id: str,
    ) -> "Execution":
        return cls(
            id=str(uuid4()),
            workflow_id=workflow_id,
            event_record_id=event_record_id,
            status=ExecutionStatus.PENDING,
            started_at=datetime.now(UTC),
            finished_at=None,
            error_message=None,
        )

    def mark_running(self) -> None:
        if self.status is not ExecutionStatus.PENDING:
            raise InvalidExecutionStateError("Execution can only move to running from pending")
        self.status = ExecutionStatus.RUNNING
        self.error_message = None

    def mark_success(self) -> None:
        if self.status is not ExecutionStatus.RUNNING:
            raise InvalidExecutionStateError("Execution can only succeed from running")
        self.status = ExecutionStatus.SUCCESS
        self.finished_at = datetime.now(UTC)
        self.error_message = None

    def mark_failed(self, error_message: str) -> None:
        if self.status not in {ExecutionStatus.PENDING, ExecutionStatus.RUNNING}:
            raise InvalidExecutionStateError("Execution can only fail from pending or running")
        self.status = ExecutionStatus.FAILED
        self.finished_at = datetime.now(UTC)
        self.error_message = error_message
