from __future__ import annotations

from app.core.exceptions import TraceflowError


class WorkflowNotFoundError(TraceflowError):
    code = "workflow_not_found"
    message = "Workflow not found"


class ForbiddenResourceAccessError(TraceflowError):
    code = "forbidden_resource_access"
    message = "Forbidden resource access"


class ActiveWorkflowConflictError(TraceflowError):
    code = "active_workflow_conflict"
    message = "An active workflow already exists for this event type"


class InvalidWorkflowDataError(TraceflowError):
    code = "invalid_workflow_data"
    message = "Workflow data is invalid"
