from __future__ import annotations

from typing import Protocol

from app.domain.entities import Workflow


class WorkflowRepository(Protocol):
    def get_by_id(self, workflow_id: str) -> Workflow | None: ...

    def get_active_by_owner_and_event_type(
        self,
        *,
        owner_id: str,
        event_type: str,
    ) -> Workflow | None: ...

    def list_by_owner(
        self,
        *,
        owner_id: str,
        page: int,
        page_size: int,
        is_active: bool | None,
        event_type: str | None,
    ) -> tuple[list[Workflow], int]: ...

    def exists_active_by_owner_and_event_type(
        self,
        *,
        owner_id: str,
        event_type: str,
        exclude_workflow_id: str | None = None,
    ) -> bool: ...

    def add(self, workflow: Workflow) -> Workflow: ...

    def update(self, workflow: Workflow) -> Workflow: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
