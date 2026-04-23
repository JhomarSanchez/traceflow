from __future__ import annotations

from app.application.interfaces.repositories import WorkflowRepository
from app.domain.entities import Workflow
from app.domain.exceptions import (
    ActiveWorkflowConflictError,
    ForbiddenResourceAccessError,
    WorkflowNotFoundError,
)


class UpdateWorkflow:
    def __init__(self, workflow_repository: WorkflowRepository) -> None:
        self.workflow_repository = workflow_repository

    def __call__(
        self,
        *,
        workflow_id: str,
        owner_id: str,
        name: str | None = None,
        description: str | None = None,
        description_provided: bool = False,
        event_type: str | None = None,
    ) -> Workflow:
        workflow = self.workflow_repository.get_by_id(workflow_id)
        if workflow is None:
            raise WorkflowNotFoundError()
        if not workflow.belongs_to(owner_id):
            raise ForbiddenResourceAccessError()

        candidate_event_type = event_type if event_type is not None else workflow.event_type
        if workflow.is_active and self.workflow_repository.exists_active_by_owner_and_event_type(
            owner_id=owner_id,
            event_type=candidate_event_type.strip(),
            exclude_workflow_id=workflow.id,
        ):
            raise ActiveWorkflowConflictError()

        if name is not None:
            workflow.rename(name)
        if description_provided:
            workflow.change_description(description)
        if event_type is not None:
            workflow.change_event_type(event_type)

        try:
            updated_workflow = self.workflow_repository.update(workflow)
            self.workflow_repository.commit()
        except Exception:
            self.workflow_repository.rollback()
            raise

        return updated_workflow
