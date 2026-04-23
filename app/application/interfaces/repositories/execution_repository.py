from __future__ import annotations

from typing import Protocol

from app.domain.entities import Execution


class ExecutionRepository(Protocol):
    def get_by_id(self, execution_id: str) -> Execution | None: ...

    def add(self, execution: Execution) -> Execution: ...

    def update(self, execution: Execution) -> Execution: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
