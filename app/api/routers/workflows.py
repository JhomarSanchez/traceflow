from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_current_user, get_workflow_repository
from app.api.schemas.workflows import (
    CreateWorkflowRequest,
    UpdateWorkflowRequest,
    WorkflowListResponse,
    WorkflowResponse,
    WorkflowStatusResponse,
)
from app.application.use_cases.workflows import (
    ActivateWorkflow,
    CreateWorkflow,
    DeactivateWorkflow,
    GetWorkflowDetail,
    ListWorkflows,
    UpdateWorkflow,
)
from app.domain.entities import User
from app.infrastructure.db.repositories import SqlAlchemyWorkflowRepository

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
def create_workflow(
    payload: CreateWorkflowRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    workflow_repository: Annotated[
        SqlAlchemyWorkflowRepository, Depends(get_workflow_repository)
    ],
) -> WorkflowResponse:
    use_case = CreateWorkflow(workflow_repository)
    workflow = use_case(
        owner_id=current_user.id,
        name=payload.name,
        description=payload.description,
        event_type=payload.event_type,
    )
    return WorkflowResponse.model_validate(workflow)


@router.get("", response_model=WorkflowListResponse)
def list_workflows(
    current_user: Annotated[User, Depends(get_current_user)],
    workflow_repository: Annotated[
        SqlAlchemyWorkflowRepository, Depends(get_workflow_repository)
    ],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    is_active: bool | None = Query(default=None),
    event_type: str | None = Query(default=None),
) -> WorkflowListResponse:
    use_case = ListWorkflows(workflow_repository)
    items, total = use_case(
        owner_id=current_user.id,
        page=page,
        page_size=page_size,
        is_active=is_active,
        event_type=event_type,
    )
    return WorkflowListResponse(
        items=[WorkflowResponse.model_validate(item) for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow_detail(
    workflow_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    workflow_repository: Annotated[
        SqlAlchemyWorkflowRepository, Depends(get_workflow_repository)
    ],
) -> WorkflowResponse:
    use_case = GetWorkflowDetail(workflow_repository)
    workflow = use_case(workflow_id=workflow_id, owner_id=current_user.id)
    return WorkflowResponse.model_validate(workflow)


@router.patch("/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(
    workflow_id: str,
    payload: UpdateWorkflowRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    workflow_repository: Annotated[
        SqlAlchemyWorkflowRepository, Depends(get_workflow_repository)
    ],
) -> WorkflowResponse:
    use_case = UpdateWorkflow(workflow_repository)
    updates = payload.model_dump(exclude_unset=True)
    workflow = use_case(
        workflow_id=workflow_id,
        owner_id=current_user.id,
        name=updates.get("name"),
        description=updates.get("description"),
        description_provided="description" in updates,
        event_type=updates.get("event_type"),
    )
    return WorkflowResponse.model_validate(workflow)


@router.post("/{workflow_id}/activate", response_model=WorkflowStatusResponse)
def activate_workflow(
    workflow_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    workflow_repository: Annotated[
        SqlAlchemyWorkflowRepository, Depends(get_workflow_repository)
    ],
) -> WorkflowStatusResponse:
    use_case = ActivateWorkflow(workflow_repository)
    workflow = use_case(workflow_id=workflow_id, owner_id=current_user.id)
    return WorkflowStatusResponse(id=workflow.id, is_active=workflow.is_active)


@router.post("/{workflow_id}/deactivate", response_model=WorkflowStatusResponse)
def deactivate_workflow(
    workflow_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    workflow_repository: Annotated[
        SqlAlchemyWorkflowRepository, Depends(get_workflow_repository)
    ],
) -> WorkflowStatusResponse:
    use_case = DeactivateWorkflow(workflow_repository)
    workflow = use_case(workflow_id=workflow_id, owner_id=current_user.id)
    return WorkflowStatusResponse(id=workflow.id, is_active=workflow.is_active)
