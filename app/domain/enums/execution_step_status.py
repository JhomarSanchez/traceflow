from __future__ import annotations

from enum import Enum


class ExecutionStepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
