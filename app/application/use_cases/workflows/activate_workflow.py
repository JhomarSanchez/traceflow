from __future__ import annotations

from app.application.interfaces.repositories import WorkflowRepository
from app.domain.entities import Workflow
from app.domain.exceptions import (
    ActiveWorkflowConflictError,
    ForbiddenResourceAccessError,
    WorkflowNotFoundError,
)


class ActivateWorkflow:
    def __init__(self, workflow_repository: WorkflowRepository) -> None:
        self.workflow_repository = workflow_repository

    def __call__(self, *, workflow_id: str, owner_id: str) -> Workflow:
        workflow = self.workflow_repository.get_by_id(workflow_id)
        if workflow is None:
            raise WorkflowNotFoundError()
        if not workflow.belongs_to(owner_id):
            raise ForbiddenResourceAccessError()
        if self.workflow_repository.exists_active_by_owner_and_event_type(
            owner_id=owner_id,
            event_type=workflow.event_type,
            exclude_workflow_id=workflow.id,
        ):
            raise ActiveWorkflowConflictError()

        workflow.activate()

        try:
            updated_workflow = self.workflow_repository.update(workflow)
            self.workflow_repository.commit()
        except Exception:
            self.workflow_repository.rollback()
            raise

        return updated_workflow
