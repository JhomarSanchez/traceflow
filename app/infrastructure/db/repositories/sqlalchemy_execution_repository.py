from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.entities import Execution
from app.domain.enums import ExecutionStatus
from app.infrastructure.db.models.execution import ExecutionModel


class SqlAlchemyExecutionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, execution_id: str) -> Execution | None:
        model = self.session.get(ExecutionModel, execution_id)
        return self._to_domain(model) if model is not None else None

    def add(self, execution: Execution) -> Execution:
        model = ExecutionModel(
            id=execution.id,
            workflow_id=execution.workflow_id,
            event_record_id=execution.event_record_id,
            status=execution.status.value,
            started_at=execution.started_at,
            finished_at=execution.finished_at,
            error_message=execution.error_message,
        )
        self.session.add(model)
        self.session.flush()
        return self._to_domain(model)

    def update(self, execution: Execution) -> Execution:
        model = self.session.get(ExecutionModel, execution.id)
        if model is None:
            return execution

        model.status = execution.status.value
        model.started_at = execution.started_at
        model.finished_at = execution.finished_at
        model.error_message = execution.error_message
        self.session.flush()
        return self._to_domain(model)

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    @staticmethod
    def _to_domain(model: ExecutionModel) -> Execution:
        return Execution(
            id=model.id,
            workflow_id=model.workflow_id,
            event_record_id=model.event_record_id,
            status=ExecutionStatus(model.status),
            started_at=model.started_at,
            finished_at=model.finished_at,
            error_message=model.error_message,
        )
