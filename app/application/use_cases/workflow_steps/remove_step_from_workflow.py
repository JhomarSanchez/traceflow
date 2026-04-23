from __future__ import annotations

from app.application.interfaces.repositories import WorkflowRepository, WorkflowStepRepository
from app.domain.exceptions import (
    ForbiddenResourceAccessError,
    WorkflowNotFoundError,
    WorkflowStepNotFoundError,
)


class RemoveStepFromWorkflow:
    def __init__(
        self,
        workflow_repository: WorkflowRepository,
        workflow_step_repository: WorkflowStepRepository,
    ) -> None:
        self.workflow_repository = workflow_repository
        self.workflow_step_repository = workflow_step_repository

    def __call__(self, *, workflow_id: str, step_id: str, owner_id: str) -> None:
        workflow = self.workflow_repository.get_by_id(workflow_id)
        if workflow is None:
            raise WorkflowNotFoundError()
        if not workflow.belongs_to(owner_id):
            raise ForbiddenResourceAccessError()

        workflow_step = self.workflow_step_repository.get_by_id_and_workflow(
            step_id=step_id,
            workflow_id=workflow_id,
        )
        if workflow_step is None:
            raise WorkflowStepNotFoundError()

        try:
            self.workflow_step_repository.delete(workflow_step)
            self.workflow_step_repository.commit()
        except Exception:
            self.workflow_step_repository.rollback()
            raise
