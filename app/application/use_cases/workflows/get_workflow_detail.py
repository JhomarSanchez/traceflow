from __future__ import annotations

from app.application.interfaces.repositories import WorkflowRepository
from app.domain.entities import Workflow
from app.domain.exceptions import ForbiddenResourceAccessError, WorkflowNotFoundError


class GetWorkflowDetail:
    def __init__(self, workflow_repository: WorkflowRepository) -> None:
        self.workflow_repository = workflow_repository

    def __call__(self, *, workflow_id: str, owner_id: str) -> Workflow:
        workflow = self.workflow_repository.get_by_id(workflow_id)
        if workflow is None:
            raise WorkflowNotFoundError()
        if not workflow.belongs_to(owner_id):
            raise ForbiddenResourceAccessError()
        return workflow
