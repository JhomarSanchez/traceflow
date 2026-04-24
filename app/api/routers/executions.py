from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import (
    get_current_user,
    get_execution_repository,
    get_execution_step_repository,
)
from app.api.schemas.executions import (
    ExecutionDetailResponse,
    ExecutionListResponse,
    ExecutionResponse,
    ExecutionStepResponse,
)
from app.application.use_cases.executions import GetExecutionDetail, ListExecutions
from app.domain.entities import User
from app.domain.enums import ExecutionStatus
from app.infrastructure.db.repositories import (
    SqlAlchemyExecutionRepository,
    SqlAlchemyExecutionStepRepository,
)

router = APIRouter(prefix="/executions", tags=["executions"])


@router.get("", response_model=ExecutionListResponse)
def list_executions(
    current_user: Annotated[User, Depends(get_current_user)],
    execution_repository: Annotated[
        SqlAlchemyExecutionRepository, Depends(get_execution_repository)
    ],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: ExecutionStatus | None = Query(default=None),
    workflow_id: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
) -> ExecutionListResponse:
    use_case = ListExecutions(execution_repository)
    items, total = use_case(
        owner_id=current_user.id,
        page=page,
        page_size=page_size,
        status=status,
        workflow_id=workflow_id,
        event_type=event_type,
    )
    return ExecutionListResponse(
        items=[ExecutionResponse.model_validate(item) for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{execution_id}", response_model=ExecutionDetailResponse)
def get_execution_detail(
    execution_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    execution_repository: Annotated[
        SqlAlchemyExecutionRepository, Depends(get_execution_repository)
    ],
    execution_step_repository: Annotated[
        SqlAlchemyExecutionStepRepository, Depends(get_execution_step_repository)
    ],
) -> ExecutionDetailResponse:
    use_case = GetExecutionDetail(execution_repository, execution_step_repository)
    execution, steps = use_case(execution_id=execution_id, owner_id=current_user.id)
    return ExecutionDetailResponse(
        id=execution.id,
        workflow_id=execution.workflow_id,
        event_record_id=execution.event_record_id,
        status=execution.status,
        started_at=execution.started_at,
        finished_at=execution.finished_at,
        error_message=execution.error_message,
        steps=[ExecutionStepResponse.model_validate(step) for step in steps],
    )
