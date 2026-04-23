from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.entities import WorkflowStep, normalize_step_config, normalize_step_type
from app.domain.exceptions import StepOrderConflictError
from app.infrastructure.db.models.workflow_step import WorkflowStepModel


class SqlAlchemyWorkflowStepRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, step_id: str) -> WorkflowStep | None:
        model = self.session.get(WorkflowStepModel, step_id)
        return self._to_domain(model) if model is not None else None

    def get_by_id_and_workflow(
        self,
        *,
        step_id: str,
        workflow_id: str,
    ) -> WorkflowStep | None:
        statement = select(WorkflowStepModel).where(
            WorkflowStepModel.id == step_id,
            WorkflowStepModel.workflow_id == workflow_id,
        )
        model = self.session.scalar(statement)
        return self._to_domain(model) if model is not None else None

    def list_by_workflow_id(self, *, workflow_id: str) -> list[WorkflowStep]:
        statement = (
            select(WorkflowStepModel)
            .where(WorkflowStepModel.workflow_id == workflow_id)
            .order_by(WorkflowStepModel.step_order.asc(), WorkflowStepModel.created_at.asc())
        )
        return [self._to_domain(model) for model in self.session.scalars(statement).all()]

    def exists_step_order(
        self,
        *,
        workflow_id: str,
        step_order: int,
    ) -> bool:
        statement = select(WorkflowStepModel.id).where(
            WorkflowStepModel.workflow_id == workflow_id,
            WorkflowStepModel.step_order == step_order,
        )
        return self.session.scalar(statement) is not None

    def add(self, workflow_step: WorkflowStep) -> WorkflowStep:
        model = WorkflowStepModel(
            id=workflow_step.id,
            workflow_id=workflow_step.workflow_id,
            step_order=workflow_step.step_order,
            step_type=workflow_step.step_type.value,
            step_config=workflow_step.step_config,
            created_at=workflow_step.created_at,
        )
        self.session.add(model)
        self._flush_with_conflict_translation()
        return self._to_domain(model)

    def delete(self, workflow_step: WorkflowStep) -> None:
        model = self.session.get(WorkflowStepModel, workflow_step.id)
        if model is not None:
            self.session.delete(model)

    def commit(self) -> None:
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise StepOrderConflictError() from exc

    def rollback(self) -> None:
        self.session.rollback()

    def _flush_with_conflict_translation(self) -> None:
        try:
            self.session.flush()
        except IntegrityError as exc:
            self.session.rollback()
            raise StepOrderConflictError() from exc

    @staticmethod
    def _to_domain(model: WorkflowStepModel) -> WorkflowStep:
        return WorkflowStep(
            id=model.id,
            workflow_id=model.workflow_id,
            step_order=model.step_order,
            step_type=normalize_step_type(model.step_type),
            step_config=normalize_step_config(model.step_config),
            created_at=model.created_at,
        )
