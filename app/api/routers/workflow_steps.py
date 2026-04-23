from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.api.dependencies import (
    get_current_user,
    get_workflow_repository,
    get_workflow_step_repository,
)
from app.api.schemas.workflow_steps import (
    CreateWorkflowStepRequest,
    WorkflowStepListResponse,
    WorkflowStepResponse,
)
from app.application.use_cases.workflow_steps import (
    AddStepToWorkflow,
    ListWorkflowSteps,
    RemoveStepFromWorkflow,
)
from app.domain.entities import User
from app.infrastructure.db.repositories import (
    SqlAlchemyWorkflowRepository,
    SqlAlchemyWorkflowStepRepository,
)

router = APIRouter(prefix="/workflows/{workflow_id}/steps", tags=["workflow-steps"])


@router.post("", response_model=WorkflowStepResponse, status_code=status.HTTP_201_CREATED)
def add_workflow_step(
    workflow_id: str,
    payload: CreateWorkflowStepRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    workflow_repository: Annotated[
        SqlAlchemyWorkflowRepository, Depends(get_workflow_repository)
    ],
    workflow_step_repository: Annotated[
        SqlAlchemyWorkflowStepRepository, Depends(get_workflow_step_repository)
    ],
) -> WorkflowStepResponse:
    use_case = AddStepToWorkflow(workflow_repository, workflow_step_repository)
    workflow_step = use_case(
        workflow_id=workflow_id,
        owner_id=current_user.id,
        step_order=payload.step_order,
        step_type=payload.step_type,
        step_config=payload.step_config,
    )
    return WorkflowStepResponse.model_validate(workflow_step)


@router.get("", response_model=WorkflowStepListResponse)
def list_workflow_steps(
    workflow_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    workflow_repository: Annotated[
        SqlAlchemyWorkflowRepository, Depends(get_workflow_repository)
    ],
    workflow_step_repository: Annotated[
        SqlAlchemyWorkflowStepRepository, Depends(get_workflow_step_repository)
    ],
) -> WorkflowStepListResponse:
    use_case = ListWorkflowSteps(workflow_repository, workflow_step_repository)
    items = use_case(workflow_id=workflow_id, owner_id=current_user.id)
    return WorkflowStepListResponse(
        items=[WorkflowStepResponse.model_validate(item) for item in items]
    )


@router.delete("/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_workflow_step(
    workflow_id: str,
    step_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    workflow_repository: Annotated[
        SqlAlchemyWorkflowRepository, Depends(get_workflow_repository)
    ],
    workflow_step_repository: Annotated[
        SqlAlchemyWorkflowStepRepository, Depends(get_workflow_step_repository)
    ],
) -> Response:
    use_case = RemoveStepFromWorkflow(workflow_repository, workflow_step_repository)
    use_case(workflow_id=workflow_id, step_id=step_id, owner_id=current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
