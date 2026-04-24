from __future__ import annotations

from typing import Protocol

from app.domain.entities import Execution
from app.domain.enums import ExecutionStatus


class ExecutionRepository(Protocol):
    def get_by_id(self, execution_id: str) -> Execution | None: ...

    def is_owned_by(self, *, execution_id: str, owner_id: str) -> bool: ...

    def list_by_owner(
        self,
        *,
        owner_id: str,
        page: int,
        page_size: int,
        status: ExecutionStatus | None,
        workflow_id: str | None,
        event_type: str | None,
    ) -> tuple[list[Execution], int]: ...

    def add(self, execution: Execution) -> Execution: ...

    def update(self, execution: Execution) -> Execution: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
