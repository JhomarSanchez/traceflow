from __future__ import annotations

from app.application.interfaces.repositories import WorkflowRepository
from app.domain.entities import Workflow
from app.domain.exceptions import ActiveWorkflowConflictError


class CreateWorkflow:
    def __init__(self, workflow_repository: WorkflowRepository) -> None:
        self.workflow_repository = workflow_repository

    def __call__(
        self,
        *,
        owner_id: str,
        name: str,
        description: str | None,
        event_type: str,
    ) -> Workflow:
        if self.workflow_repository.exists_active_by_owner_and_event_type(
            owner_id=owner_id,
            event_type=event_type.strip(),
        ):
            raise ActiveWorkflowConflictError()

        workflow = Workflow.create(
            owner_id=owner_id,
            name=name,
            description=description,
            event_type=event_type,
        )

        try:
            self.workflow_repository.add(workflow)
            self.workflow_repository.commit()
        except Exception:
            self.workflow_repository.rollback()
            raise

        return workflow
