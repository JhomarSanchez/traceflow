from __future__ import annotations

from typing import Protocol

from app.domain.entities import WorkflowStep


class WorkflowStepRepository(Protocol):
    def get_by_id(self, step_id: str) -> WorkflowStep | None: ...

    def get_by_id_and_workflow(
        self,
        *,
        step_id: str,
        workflow_id: str,
    ) -> WorkflowStep | None: ...

    def list_by_workflow_id(self, *, workflow_id: str) -> list[WorkflowStep]: ...

    def exists_step_order(
        self,
        *,
        workflow_id: str,
        step_order: int,
    ) -> bool: ...

    def add(self, workflow_step: WorkflowStep) -> WorkflowStep: ...

    def delete(self, workflow_step: WorkflowStep) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
