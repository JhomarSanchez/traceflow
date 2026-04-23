from __future__ import annotations

from enum import Enum


class WorkflowStepType(str, Enum):
    LOG_MESSAGE = "log_message"
    PERSIST_PAYLOAD = "persist_payload"
    MARK_SUCCESS = "mark_success"
    TRANSFORM_PAYLOAD = "transform_payload"
