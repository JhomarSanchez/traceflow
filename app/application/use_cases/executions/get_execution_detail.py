from __future__ import annotations

from app.application.interfaces.repositories import ExecutionRepository, ExecutionStepRepository
from app.domain.entities import Execution, ExecutionStep
from app.domain.exceptions import (
    ExecutionNotFoundError,
    ForbiddenResourceAccessError,
)


class GetExecutionDetail:
    def __init__(
        self,
        execution_repository: ExecutionRepository,
        execution_step_repository: ExecutionStepRepository,
    ) -> None:
        self.execution_repository = execution_repository
        self.execution_step_repository = execution_step_repository

    def __call__(
        self,
        *,
        execution_id: str,
        owner_id: str,
    ) -> tuple[Execution, list[ExecutionStep]]:
        execution = self.execution_repository.get_by_id(execution_id)
        if execution is None:
            raise ExecutionNotFoundError()
        if not self.execution_repository.is_owned_by(
            execution_id=execution_id,
            owner_id=owner_id,
        ):
            raise ForbiddenResourceAccessError()

        execution_steps = self.execution_step_repository.list_by_execution_id(
            execution_id=execution_id
        )
        return execution, execution_steps
