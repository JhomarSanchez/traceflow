from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import WorkflowStepType


class CreateWorkflowStepRequest(BaseModel):
    step_order: int = Field(ge=1)
    step_type: WorkflowStepType
    step_config: dict[str, Any]


class WorkflowStepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workflow_id: str
    step_order: int
    step_type: WorkflowStepType
    step_config: dict[str, Any]
    created_at: datetime


class WorkflowStepListResponse(BaseModel):
    items: list[WorkflowStepResponse]
