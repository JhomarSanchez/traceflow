from __future__ import annotations

from app.application.interfaces.repositories import WorkflowRepository
from app.domain.entities import Workflow
from app.domain.exceptions import InvalidWorkflowDataError


class ListWorkflows:
    def __init__(self, workflow_repository: WorkflowRepository) -> None:
        self.workflow_repository = workflow_repository

    def __call__(
        self,
        *,
        owner_id: str,
        page: int,
        page_size: int,
        is_active: bool | None,
        event_type: str | None,
    ) -> tuple[list[Workflow], int]:
        normalized_event_type = None
        if event_type is not None:
            normalized_event_type = event_type.strip()
            if not normalized_event_type:
                raise InvalidWorkflowDataError("Workflow event_type must not be empty")

        return self.workflow_repository.list_by_owner(
            owner_id=owner_id,
            page=page,
            page_size=page_size,
            is_active=is_active,
            event_type=normalized_event_type,
        )
