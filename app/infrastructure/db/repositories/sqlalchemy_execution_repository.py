from __future__ import annotations

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.domain.entities import Execution
from app.domain.enums import ExecutionStatus
from app.infrastructure.db.models.event_record import EventRecordModel
from app.infrastructure.db.models.execution import ExecutionModel
from app.infrastructure.db.models.workflow import WorkflowModel


class SqlAlchemyExecutionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, execution_id: str) -> Execution | None:
        model = self.session.get(ExecutionModel, execution_id)
        return self._to_domain(model) if model is not None else None

    def is_owned_by(self, *, execution_id: str, owner_id: str) -> bool:
        statement = (
            select(ExecutionModel.id)
            .join(WorkflowModel, ExecutionModel.workflow_id == WorkflowModel.id)
            .where(
                ExecutionModel.id == execution_id,
                WorkflowModel.owner_id == owner_id,
            )
        )
        return self.session.scalar(statement) is not None

    def list_by_owner(
        self,
        *,
        owner_id: str,
        page: int,
        page_size: int,
        status: ExecutionStatus | None,
        workflow_id: str | None,
        event_type: str | None,
    ) -> tuple[list[Execution], int]:
        statement = (
            select(ExecutionModel)
            .join(WorkflowModel, ExecutionModel.workflow_id == WorkflowModel.id)
            .join(EventRecordModel, ExecutionModel.event_record_id == EventRecordModel.id)
            .where(WorkflowModel.owner_id == owner_id)
        )
        count_statement: Select[tuple[int]] = (
            select(func.count())
            .select_from(ExecutionModel)
            .join(WorkflowModel, ExecutionModel.workflow_id == WorkflowModel.id)
            .join(EventRecordModel, ExecutionModel.event_record_id == EventRecordModel.id)
            .where(WorkflowModel.owner_id == owner_id)
        )

        if status is not None:
            statement = statement.where(ExecutionModel.status == status.value)
            count_statement = count_statement.where(ExecutionModel.status == status.value)
        if workflow_id is not None:
            statement = statement.where(ExecutionModel.workflow_id == workflow_id)
            count_statement = count_statement.where(ExecutionModel.workflow_id == workflow_id)
        if event_type is not None:
            statement = statement.where(EventRecordModel.event_type == event_type)
            count_statement = count_statement.where(EventRecordModel.event_type == event_type)

        statement = statement.order_by(ExecutionModel.started_at.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size)

        models = self.session.scalars(statement).all()
        total = self.session.scalar(count_statement) or 0
        return [self._to_domain(model) for model in models], total

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
