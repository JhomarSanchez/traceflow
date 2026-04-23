from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.domain.entities import Workflow
from app.domain.exceptions import ActiveWorkflowConflictError
from app.infrastructure.db.models.workflow import WorkflowModel


class SqlAlchemyWorkflowRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, workflow_id: str) -> Workflow | None:
        model = self.session.get(WorkflowModel, workflow_id)
        return self._to_domain(model) if model is not None else None

    def list_by_owner(
        self,
        *,
        owner_id: str,
        page: int,
        page_size: int,
        is_active: bool | None,
        event_type: str | None,
    ) -> tuple[list[Workflow], int]:
        statement = select(WorkflowModel).where(WorkflowModel.owner_id == owner_id)
        count_statement: Select[tuple[int]] = select(func.count()).select_from(WorkflowModel).where(
            WorkflowModel.owner_id == owner_id
        )

        if is_active is not None:
            statement = statement.where(WorkflowModel.is_active == is_active)
            count_statement = count_statement.where(WorkflowModel.is_active == is_active)
        if event_type is not None:
            statement = statement.where(WorkflowModel.event_type == event_type)
            count_statement = count_statement.where(WorkflowModel.event_type == event_type)

        statement = statement.order_by(WorkflowModel.created_at.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size)

        models = self.session.scalars(statement).all()
        total = self.session.scalar(count_statement) or 0
        return [self._to_domain(model) for model in models], total

    def exists_active_by_owner_and_event_type(
        self,
        *,
        owner_id: str,
        event_type: str,
        exclude_workflow_id: str | None = None,
    ) -> bool:
        statement = select(WorkflowModel.id).where(
            WorkflowModel.owner_id == owner_id,
            WorkflowModel.event_type == event_type,
            WorkflowModel.is_active.is_(True),
        )
        if exclude_workflow_id is not None:
            statement = statement.where(WorkflowModel.id != exclude_workflow_id)
        return self.session.scalar(statement) is not None

    def add(self, workflow: Workflow) -> Workflow:
        model = WorkflowModel(
            id=workflow.id,
            owner_id=workflow.owner_id,
            name=workflow.name,
            description=workflow.description,
            event_type=workflow.event_type,
            is_active=workflow.is_active,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at,
        )
        self.session.add(model)
        self._flush_with_conflict_translation()
        return self._to_domain(model)

    def update(self, workflow: Workflow) -> Workflow:
        model = self.session.get(WorkflowModel, workflow.id)
        if model is None:
            return workflow

        model.name = workflow.name
        model.description = workflow.description
        model.event_type = workflow.event_type
        model.is_active = workflow.is_active
        model.updated_at = workflow.updated_at
        self._flush_with_conflict_translation()
        return self._to_domain(model)

    def commit(self) -> None:
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise ActiveWorkflowConflictError() from exc

    def rollback(self) -> None:
        self.session.rollback()

    def _flush_with_conflict_translation(self) -> None:
        try:
            self.session.flush()
        except IntegrityError as exc:
            self.session.rollback()
            raise ActiveWorkflowConflictError() from exc

    @staticmethod
    def _to_domain(model: WorkflowModel) -> Workflow:
        return Workflow(
            id=model.id,
            owner_id=model.owner_id,
            name=model.name,
            description=model.description,
            event_type=model.event_type,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
