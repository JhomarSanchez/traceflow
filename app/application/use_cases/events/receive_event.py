from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from app.application.interfaces.repositories import (
    EventRecordRepository,
    ExecutionRepository,
    WorkflowRepository,
    WorkflowStepRepository,
)
from app.application.use_cases.events.process_event import ProcessEvent
from app.domain.entities import EventRecord, Execution
from app.domain.exceptions import (
    EventTypeNotSupportedError,
    UnexpectedExecutionError,
    WorkflowHasNoStepsError,
)

logger = logging.getLogger(__name__)


class ReceiveEvent:
    def __init__(
        self,
        workflow_repository: WorkflowRepository,
        workflow_step_repository: WorkflowStepRepository,
        event_record_repository: EventRecordRepository,
        execution_repository: ExecutionRepository,
        process_event: ProcessEvent,
    ) -> None:
        self.workflow_repository = workflow_repository
        self.workflow_step_repository = workflow_step_repository
        self.event_record_repository = event_record_repository
        self.execution_repository = execution_repository
        self.process_event = process_event

    def __call__(
        self,
        *,
        owner_id: str,
        event_type: str,
        payload: Mapping[str, Any],
    ) -> tuple[EventRecord, Execution]:
        logger.info("event_received owner_id=%s event_type=%s", owner_id, event_type.strip())

        workflow = self.workflow_repository.get_active_by_owner_and_event_type(
            owner_id=owner_id,
            event_type=event_type.strip(),
        )
        if workflow is None:
            raise EventTypeNotSupportedError()
        logger.info(
            "workflow_resolved owner_id=%s workflow_id=%s event_type=%s",
            owner_id,
            workflow.id,
            workflow.event_type,
        )

        workflow_steps = self.workflow_step_repository.list_by_workflow_id(
            workflow_id=workflow.id
        )
        event_record = EventRecord.create(
            workflow_id=workflow.id,
            event_type=event_type,
            payload=payload,
            received_by_user_id=owner_id,
        )
        execution = Execution.create(
            workflow_id=workflow.id,
            event_record_id=event_record.id,
        )

        try:
            self.event_record_repository.add(event_record)
            self.execution_repository.add(execution)

            if not workflow_steps:
                execution.mark_failed("Workflow has no steps")
                self.execution_repository.update(execution)
                self.execution_repository.commit()
                logger.warning(
                    "execution_rejected_no_steps execution_id=%s workflow_id=%s",
                    execution.id,
                    workflow.id,
                )
                raise WorkflowHasNoStepsError()

            processed_execution = self.process_event(
                execution=execution,
                workflow_steps=workflow_steps,
                payload=payload,
            )
            self.execution_repository.commit()
            logger.info(
                "event_processed execution_id=%s workflow_id=%s status=%s",
                processed_execution.id,
                processed_execution.workflow_id,
                processed_execution.status.value,
            )
            return event_record, processed_execution
        except WorkflowHasNoStepsError:
            raise
        except UnexpectedExecutionError:
            self.execution_repository.commit()
            raise
        except Exception:
            self.execution_repository.rollback()
            raise
