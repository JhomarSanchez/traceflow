from __future__ import annotations

from app.core.exceptions import TraceflowError


class ExecutionNotFoundError(TraceflowError):
    code = "execution_not_found"
    message = "Execution not found"


class InvalidExecutionStateError(TraceflowError):
    code = "invalid_execution_state"
    message = "Execution state is invalid"


class InvalidExecutionFilterError(TraceflowError):
    code = "invalid_execution_filter"
    message = "Execution filter is invalid"
