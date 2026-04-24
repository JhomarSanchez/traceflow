from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import TraceflowError

ERROR_STATUS_CODES = {
    "active_workflow_conflict": 409,
    "authentication_required": 401,
    "email_already_exists": 409,
    "event_type_not_supported": 404,
    "execution_not_found": 404,
    "forbidden_resource_access": 403,
    "inactive_user": 401,
    "invalid_credentials": 401,
    "invalid_event_payload": 422,
    "invalid_execution_filter": 422,
    "invalid_token": 401,
    "invalid_execution_state": 500,
    "invalid_workflow_data": 422,
    "step_order_conflict": 409,
    "traceflow_error": 500,
    "unexpected_execution_error": 500,
    "validation_error": 422,
    "workflow_has_no_steps": 409,
    "workflow_not_found": 404,
    "workflow_step_not_found": 404,
}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(TraceflowError)
    async def handle_traceflow_error(
        _: Request,
        exc: TraceflowError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=ERROR_STATUS_CODES.get(exc.code, 500),
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Validation error",
                    "details": exc.errors(),
                }
            },
        )
