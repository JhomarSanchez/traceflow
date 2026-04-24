from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from app.application.interfaces.repositories import (
    ExecutionRepository,
    ExecutionStepRepository,
)
from app.domain.entities import Execution, ExecutionStep, WorkflowStep, normalize_event_payload
from app.domain.enums import WorkflowStepType
from app.domain.exceptions import UnexpectedExecutionError

logger = logging.getLogger(__name__)


class ProcessEvent:
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
        execution: Execution,
        workflow_steps: list[WorkflowStep],
        payload: Mapping[str, Any],
    ) -> Execution:
        current_payload = normalize_event_payload(payload)

        execution.mark_running()
        self.execution_repository.update(execution)
        logger.info(
            "execution_started execution_id=%s workflow_id=%s",
            execution.id,
            execution.workflow_id,
        )

        for workflow_step in workflow_steps:
            execution_step = ExecutionStep.create(
                execution_id=execution.id,
                workflow_step_id=workflow_step.id,
                input_data=current_payload,
            )
            self.execution_step_repository.add(execution_step)
            execution_step.mark_running()
            self.execution_step_repository.update(execution_step)

            try:
                current_payload, output_data = self._execute_step(
                    workflow_step=workflow_step,
                    payload=current_payload,
                )
            except Exception as exc:
                message = str(exc) or "Workflow step execution failed"
                execution_step.mark_failed(message)
                self.execution_step_repository.update(execution_step)
                execution.mark_failed(message)
                self.execution_repository.update(execution)
                logger.exception(
                    "execution_failed execution_id=%s workflow_id=%s workflow_step_id=%s",
                    execution.id,
                    execution.workflow_id,
                    workflow_step.id,
                )
                raise UnexpectedExecutionError(
                    details={
                        "execution_id": execution.id,
                        "workflow_step_id": workflow_step.id,
                    }
                ) from exc

            execution_step.mark_success(output_data)
            self.execution_step_repository.update(execution_step)
            logger.info(
                "workflow_step_completed execution_id=%s workflow_step_id=%s step_type=%s",
                execution.id,
                workflow_step.id,
                workflow_step.step_type.value,
            )

        execution.mark_success()
        self.execution_repository.update(execution)
        logger.info(
            "execution_succeeded execution_id=%s workflow_id=%s",
            execution.id,
            execution.workflow_id,
        )
        return execution

    def _execute_step(
        self,
        *,
        workflow_step: WorkflowStep,
        payload: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        if workflow_step.step_type is WorkflowStepType.LOG_MESSAGE:
            message = workflow_step.step_config.get("message", "Workflow step executed")
            if not isinstance(message, str) or not message.strip():
                raise ValueError("log_message step requires a non-empty message")
            logger.info(
                "workflow_step_log workflow_step_id=%s message=%s",
                workflow_step.id,
                message.strip(),
            )
            return payload, {"message": message.strip()}

        if workflow_step.step_type is WorkflowStepType.PERSIST_PAYLOAD:
            return payload, {"persisted": True}

        if workflow_step.step_type is WorkflowStepType.MARK_SUCCESS:
            return payload, {"marked_success": True}

        if workflow_step.step_type is WorkflowStepType.TRANSFORM_PAYLOAD:
            set_fields = workflow_step.step_config.get("set_fields")
            if not isinstance(set_fields, Mapping):
                raise ValueError("transform_payload step requires a set_fields object")
            updated_payload = dict(payload)
            updated_payload.update(dict(set_fields))
            return updated_payload, {"payload": updated_payload}

        raise ValueError("Unsupported workflow step type")
