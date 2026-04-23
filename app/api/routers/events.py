from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import (
    get_current_user,
    get_event_record_repository,
    get_execution_repository,
    get_execution_step_repository,
    get_workflow_repository,
    get_workflow_step_repository,
)
from app.api.schemas.events import EventExecutionResponse, ReceiveEventRequest
from app.application.use_cases.events import ProcessEvent, ReceiveEvent
from app.domain.entities import User
from app.infrastructure.db.repositories import (
    SqlAlchemyEventRecordRepository,
    SqlAlchemyExecutionRepository,
    SqlAlchemyExecutionStepRepository,
    SqlAlchemyWorkflowRepository,
    SqlAlchemyWorkflowStepRepository,
)

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventExecutionResponse, status_code=status.HTTP_201_CREATED)
def receive_event(
    payload: ReceiveEventRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    workflow_repository: Annotated[
        SqlAlchemyWorkflowRepository, Depends(get_workflow_repository)
    ],
    workflow_step_repository: Annotated[
        SqlAlchemyWorkflowStepRepository, Depends(get_workflow_step_repository)
    ],
    event_record_repository: Annotated[
        SqlAlchemyEventRecordRepository, Depends(get_event_record_repository)
    ],
    execution_repository: Annotated[
        SqlAlchemyExecutionRepository, Depends(get_execution_repository)
    ],
    execution_step_repository: Annotated[
        SqlAlchemyExecutionStepRepository, Depends(get_execution_step_repository)
    ],
) -> EventExecutionResponse:
    process_event_use_case = ProcessEvent(execution_repository, execution_step_repository)
    receive_event_use_case = ReceiveEvent(
        workflow_repository,
        workflow_step_repository,
        event_record_repository,
        execution_repository,
        process_event_use_case,
    )
    event_record, execution = receive_event_use_case(
        owner_id=current_user.id,
        event_type=payload.event_type,
        payload=payload.payload,
    )
    return EventExecutionResponse(
        execution_id=execution.id,
        workflow_id=execution.workflow_id,
        event_record_id=event_record.id,
        status=execution.status,
        started_at=execution.started_at,
        finished_at=execution.finished_at,
        error_message=execution.error_message,
    )
