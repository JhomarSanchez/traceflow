from __future__ import annotations

from app.application.interfaces.repositories import ExecutionRepository
from app.domain.entities.workflow import normalize_event_type
from app.domain.enums import ExecutionStatus
from app.domain.exceptions import InvalidExecutionFilterError


class ListExecutions:
    def __init__(self, execution_repository: ExecutionRepository) -> None:
        self.execution_repository = execution_repository

    def __call__(
        self,
        *,
        owner_id: str,
        page: int,
        page_size: int,
        status: ExecutionStatus | None,
        workflow_id: str | None,
        event_type: str | None,
    ) -> tuple[list, int]:
        normalized_event_type: str | None = None
        if event_type is not None:
            if not event_type.strip():
                raise InvalidExecutionFilterError("Execution event_type filter must not be empty")
            normalized_event_type = normalize_event_type(event_type)

        return self.execution_repository.list_by_owner(
            owner_id=owner_id,
            page=page,
            page_size=page_size,
            status=status,
            workflow_id=workflow_id,
            event_type=normalized_event_type,
        )
