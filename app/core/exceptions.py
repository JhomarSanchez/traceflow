from __future__ import annotations

from typing import Any


class TraceflowError(Exception):
    code = "traceflow_error"
    message = "Unexpected application error"

    def __init__(self, message: str | None = None, *, details: Any = None) -> None:
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)


class TokenValidationError(TraceflowError):
    code = "invalid_token"
    message = "Invalid authentication token"
