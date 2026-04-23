from __future__ import annotations

from typing import Any

from app.application.interfaces.repositories import WorkflowRepository, WorkflowStepRepository
from app.domain.entities import WorkflowStep
from app.domain.enums import WorkflowStepType
from app.domain.exceptions import (
    ForbiddenResourceAccessError,
    StepOrderConflictError,
    WorkflowNotFoundError,
)


class AddStepToWorkflow:
    def __init__(
        self,
        workflow_repository: WorkflowRepository,
        workflow_step_repository: WorkflowStepRepository,
    ) -> None:
        self.workflow_repository = workflow_repository
        self.workflow_step_repository = workflow_step_repository

    def __call__(
        self,
        *,
        workflow_id: str,
        owner_id: str,
        step_order: int,
        step_type: WorkflowStepType,
        step_config: dict[str, Any],
    ) -> WorkflowStep:
        workflow = self.workflow_repository.get_by_id(workflow_id)
        if workflow is None:
            raise WorkflowNotFoundError()
        if not workflow.belongs_to(owner_id):
            raise ForbiddenResourceAccessError()
        if self.workflow_step_repository.exists_step_order(
            workflow_id=workflow_id,
            step_order=step_order,
        ):
            raise StepOrderConflictError()

        workflow_step = WorkflowStep.create(
            workflow_id=workflow_id,
            step_order=step_order,
            step_type=step_type,
            step_config=step_config,
        )

        try:
            created_step = self.workflow_step_repository.add(workflow_step)
            self.workflow_step_repository.commit()
        except Exception:
            self.workflow_step_repository.rollback()
            raise

        return created_step
