from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from app.domain.enums import WorkflowStepType
from app.domain.exceptions import InvalidWorkflowDataError


def normalize_step_order(step_order: int) -> int:
    if step_order < 1:
        raise InvalidWorkflowDataError("Workflow step_order must be greater than zero")
    return step_order


def normalize_step_type(step_type: WorkflowStepType | str) -> WorkflowStepType:
    if isinstance(step_type, WorkflowStepType):
        return step_type

    normalized = step_type.strip()
    if not normalized:
        raise InvalidWorkflowDataError("Workflow step_type must not be empty")

    try:
        return WorkflowStepType(normalized)
    except ValueError as exc:
        raise InvalidWorkflowDataError("Workflow step_type is not supported") from exc


def normalize_step_config(step_config: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(step_config, Mapping):
        raise InvalidWorkflowDataError("Workflow step_config must be an object")
    return dict(step_config)


@dataclass(slots=True)
class WorkflowStep:
    id: str
    workflow_id: str
    step_order: int
    step_type: WorkflowStepType
    step_config: dict[str, Any]
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        workflow_id: str,
        step_order: int,
        step_type: WorkflowStepType | str,
        step_config: Mapping[str, Any],
    ) -> "WorkflowStep":
        return cls(
            id=str(uuid4()),
            workflow_id=workflow_id,
            step_order=normalize_step_order(step_order),
            step_type=normalize_step_type(step_type),
            step_config=normalize_step_config(step_config),
            created_at=datetime.now(UTC),
        )

    def belongs_to_workflow(self, workflow_id: str) -> bool:
        return self.workflow_id == workflow_id
