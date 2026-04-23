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


class StepOrderConflictError(TraceflowError):
    code = "step_order_conflict"
    message = "A workflow step already exists for this step_order"


class WorkflowStepNotFoundError(TraceflowError):
    code = "workflow_step_not_found"
    message = "Workflow step not found"
