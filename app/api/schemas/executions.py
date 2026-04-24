from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.domain.enums import ExecutionStatus, ExecutionStepStatus


class ExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workflow_id: str
    event_record_id: str
    status: ExecutionStatus
    started_at: datetime
    finished_at: datetime | None
    error_message: str | None


class ExecutionListResponse(BaseModel):
    items: list[ExecutionResponse]
    page: int
    page_size: int
    total: int


class ExecutionStepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workflow_step_id: str
    status: ExecutionStepStatus
    input_data: dict[str, Any]
    output_data: dict[str, Any] | None
    error_message: str | None
    started_at: datetime
    finished_at: datetime | None


class ExecutionDetailResponse(ExecutionResponse):
    steps: list[ExecutionStepResponse]
