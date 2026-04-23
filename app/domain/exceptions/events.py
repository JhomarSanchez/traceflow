from __future__ import annotations

from app.core.exceptions import TraceflowError


class InvalidEventPayloadError(TraceflowError):
    code = "invalid_event_payload"
    message = "Event payload is invalid"


class EventTypeNotSupportedError(TraceflowError):
    code = "event_type_not_supported"
    message = "No active workflow is available for this event type"


class WorkflowHasNoStepsError(TraceflowError):
    code = "workflow_has_no_steps"
    message = "Workflow has no steps"


class UnexpectedExecutionError(TraceflowError):
    code = "unexpected_execution_error"
    message = "Unexpected execution error"
