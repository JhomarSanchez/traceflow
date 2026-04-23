from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import ExecutionStep, normalize_event_payload
from app.domain.enums import ExecutionStepStatus
from app.infrastructure.db.models.execution_step import ExecutionStepModel


class SqlAlchemyExecutionStepRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, execution_step_id: str) -> ExecutionStep | None:
        model = self.session.get(ExecutionStepModel, execution_step_id)
        return self._to_domain(model) if model is not None else None

    def list_by_execution_id(self, *, execution_id: str) -> list[ExecutionStep]:
        statement = (
            select(ExecutionStepModel)
            .where(ExecutionStepModel.execution_id == execution_id)
            .order_by(ExecutionStepModel.started_at.asc(), ExecutionStepModel.id.asc())
        )
        return [self._to_domain(model) for model in self.session.scalars(statement).all()]

    def add(self, execution_step: ExecutionStep) -> ExecutionStep:
        model = ExecutionStepModel(
            id=execution_step.id,
            execution_id=execution_step.execution_id,
            workflow_step_id=execution_step.workflow_step_id,
            status=execution_step.status.value,
            input_data=execution_step.input_data,
            output_data=execution_step.output_data,
            error_message=execution_step.error_message,
            started_at=execution_step.started_at,
            finished_at=execution_step.finished_at,
        )
        self.session.add(model)
        self.session.flush()
        return self._to_domain(model)

    def update(self, execution_step: ExecutionStep) -> ExecutionStep:
        model = self.session.get(ExecutionStepModel, execution_step.id)
        if model is None:
            return execution_step

        model.status = execution_step.status.value
        model.input_data = execution_step.input_data
        model.output_data = execution_step.output_data
        model.error_message = execution_step.error_message
        model.started_at = execution_step.started_at
        model.finished_at = execution_step.finished_at
        self.session.flush()
        return self._to_domain(model)

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    @staticmethod
    def _to_domain(model: ExecutionStepModel) -> ExecutionStep:
        return ExecutionStep(
            id=model.id,
            execution_id=model.execution_id,
            workflow_step_id=model.workflow_step_id,
            status=ExecutionStepStatus(model.status),
            input_data=normalize_event_payload(model.input_data),
            output_data=None
            if model.output_data is None
            else normalize_event_payload(model.output_data),
            error_message=model.error_message,
            started_at=model.started_at,
            finished_at=model.finished_at,
        )
