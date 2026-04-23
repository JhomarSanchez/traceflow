from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.domain.entities.workflow import normalize_event_type
from app.domain.enums import ExecutionStatus


class ReceiveEventRequest(BaseModel):
    event_type: str = Field(min_length=1, max_length=255)
    payload: dict[str, Any]

    @field_validator("event_type")
    @classmethod
    def strip_event_type(cls, value: str) -> str:
        return normalize_event_type(value)


class EventExecutionResponse(BaseModel):
    execution_id: str
    workflow_id: str
    event_record_id: str
    status: ExecutionStatus
    started_at: datetime
    finished_at: datetime | None
    error_message: str | None
