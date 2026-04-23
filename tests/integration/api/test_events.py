from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.infrastructure.db.models.event_record import EventRecordModel
from app.infrastructure.db.models.execution import ExecutionModel
from app.infrastructure.db.models.execution_step import ExecutionStepModel
from tests.integration.api.test_workflows import authenticate_user


def create_workflow(client: TestClient, headers: dict[str, str], *, event_type: str) -> str:
    response = client.post(
        "/api/v1/workflows",
        headers=headers,
        json={"name": "Workflow", "description": None, "event_type": event_type},
    )
    return response.json()["id"]


def add_step(
    client: TestClient,
    headers: dict[str, str],
    *,
    workflow_id: str,
    step_order: int,
    step_type: str,
    step_config: dict,
) -> str:
    response = client.post(
        f"/api/v1/workflows/{workflow_id}/steps",
        headers=headers,
        json={
            "step_order": step_order,
            "step_type": step_type,
            "step_config": step_config,
        },
    )
    return response.json()["id"]


def test_receive_event_processes_matching_workflow_and_persists_trace(
    client: TestClient,
    db_session: Session,
) -> None:
    headers = authenticate_user(client, email="owner@example.com")
    workflow_id = create_workflow(client, headers, event_type="user_registered")
    persist_step_id = add_step(
        client,
        headers,
        workflow_id=workflow_id,
        step_order=1,
        step_type="persist_payload",
        step_config={},
    )
    transform_step_id = add_step(
        client,
        headers,
        workflow_id=workflow_id,
        step_order=2,
        step_type="transform_payload",
        step_config={"set_fields": {"source": "traceflow"}},
    )
    mark_success_step_id = add_step(
        client,
        headers,
        workflow_id=workflow_id,
        step_order=3,
        step_type="mark_success",
        step_config={},
    )

    response = client.post(
        "/api/v1/events",
        headers=headers,
        json={
            "event_type": "user_registered",
            "payload": {"email": "user@example.com"},
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["workflow_id"] == workflow_id
    assert body["status"] == "success"
    assert body["finished_at"] is not None
    assert body["error_message"] is None

    event_record = db_session.scalars(select(EventRecordModel)).one()
    execution = db_session.scalars(select(ExecutionModel)).one()
    execution_steps = db_session.scalars(select(ExecutionStepModel)).all()
    execution_steps_by_workflow_step_id = {
        execution_step.workflow_step_id: execution_step for execution_step in execution_steps
    }

    assert event_record.workflow_id == workflow_id
    assert event_record.payload == {"email": "user@example.com"}
    assert execution.id == body["execution_id"]
    assert execution.status == "success"
    assert len(execution_steps) == 3
    assert execution_steps_by_workflow_step_id[persist_step_id].status == "success"
    assert (
        execution_steps_by_workflow_step_id[transform_step_id].output_data["payload"]["source"]
        == "traceflow"
    )
    assert (
        execution_steps_by_workflow_step_id[mark_success_step_id].input_data["source"]
        == "traceflow"
    )


def test_receive_event_rejects_event_type_without_active_workflow_for_current_user(
    client: TestClient,
) -> None:
    owner_headers = authenticate_user(client, email="owner@example.com")
    other_headers = authenticate_user(client, email="other@example.com")
    other_workflow_id = create_workflow(client, other_headers, event_type="user_registered")
    add_step(
        client,
        other_headers,
        workflow_id=other_workflow_id,
        step_order=1,
        step_type="mark_success",
        step_config={},
    )

    response = client.post(
        "/api/v1/events",
        headers=owner_headers,
        json={
            "event_type": "user_registered",
            "payload": {"email": "user@example.com"},
        },
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "event_type_not_supported"


def test_receive_event_fails_when_workflow_has_no_steps_and_persists_failed_execution(
    client: TestClient,
    db_session: Session,
) -> None:
    headers = authenticate_user(client, email="owner@example.com")
    workflow_id = create_workflow(client, headers, event_type="user_registered")

    response = client.post(
        "/api/v1/events",
        headers=headers,
        json={
            "event_type": "user_registered",
            "payload": {"email": "user@example.com"},
        },
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "workflow_has_no_steps"

    event_record = db_session.scalars(select(EventRecordModel)).one()
    execution = db_session.scalars(select(ExecutionModel)).one()

    assert event_record.workflow_id == workflow_id
    assert execution.workflow_id == workflow_id
    assert execution.status == "failed"
    assert execution.error_message == "Workflow has no steps"


def test_receive_event_persists_failed_execution_when_step_runtime_breaks(
    client: TestClient,
    db_session: Session,
) -> None:
    headers = authenticate_user(client, email="owner@example.com")
    workflow_id = create_workflow(client, headers, event_type="user_registered")
    add_step(
        client,
        headers,
        workflow_id=workflow_id,
        step_order=1,
        step_type="transform_payload",
        step_config={"set_fields": "invalid"},
    )

    response = client.post(
        "/api/v1/events",
        headers=headers,
        json={
            "event_type": "user_registered",
            "payload": {"email": "user@example.com"},
        },
    )

    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "unexpected_execution_error"
    assert body["error"]["details"]["execution_id"]

    event_record = db_session.scalars(select(EventRecordModel)).one()
    execution = db_session.scalars(select(ExecutionModel)).one()
    execution_step = db_session.scalars(select(ExecutionStepModel)).one()

    assert event_record.workflow_id == workflow_id
    assert execution.status == "failed"
    assert execution.error_message == "transform_payload step requires a set_fields object"
    assert execution_step.status == "failed"
    assert (
        execution_step.error_message
        == "transform_payload step requires a set_fields object"
    )


def test_receive_event_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/api/v1/events",
        json={
            "event_type": "user_registered",
            "payload": {"email": "user@example.com"},
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "authentication_required"
