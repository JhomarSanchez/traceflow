from __future__ import annotations

from fastapi.testclient import TestClient

from tests.integration.api.test_events import add_step, create_workflow
from tests.integration.api.test_workflows import authenticate_user


def create_success_execution(
    client: TestClient,
    headers: dict[str, str],
    *,
    event_type: str,
) -> tuple[str, str]:
    workflow_id = create_workflow(client, headers, event_type=event_type)
    add_step(
        client,
        headers,
        workflow_id=workflow_id,
        step_order=1,
        step_type="mark_success",
        step_config={},
    )
    response = client.post(
        "/api/v1/events",
        headers=headers,
        json={"event_type": event_type, "payload": {"email": "user@example.com"}},
    )
    return workflow_id, response.json()["execution_id"]


def create_failed_execution(
    client: TestClient,
    headers: dict[str, str],
    *,
    event_type: str,
) -> tuple[str, str]:
    workflow_id = create_workflow(client, headers, event_type=event_type)
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
        json={"event_type": event_type, "payload": {"email": "user@example.com"}},
    )
    return workflow_id, response.json()["error"]["details"]["execution_id"]


def test_list_executions_returns_only_current_owner_and_supports_filters(
    client: TestClient,
) -> None:
    owner_headers = authenticate_user(client, email="owner@example.com")
    other_headers = authenticate_user(client, email="other@example.com")

    success_workflow_id, success_execution_id = create_success_execution(
        client,
        owner_headers,
        event_type="user_registered",
    )
    failed_workflow_id, failed_execution_id = create_failed_execution(
        client,
        owner_headers,
        event_type="order_created",
    )
    create_success_execution(client, other_headers, event_type="user_registered")

    list_response = client.get("/api/v1/executions", headers=owner_headers)
    failed_filter_response = client.get(
        "/api/v1/executions?status=failed",
        headers=owner_headers,
    )
    workflow_filter_response = client.get(
        f"/api/v1/executions?workflow_id={success_workflow_id}",
        headers=owner_headers,
    )
    event_type_filter_response = client.get(
        "/api/v1/executions?event_type=order_created",
        headers=owner_headers,
    )
    pagination_response = client.get(
        "/api/v1/executions?page=2&page_size=1",
        headers=owner_headers,
    )

    assert list_response.status_code == 200
    list_body = list_response.json()
    assert list_body["total"] == 2
    assert {item["id"] for item in list_body["items"]} == {
        success_execution_id,
        failed_execution_id,
    }

    assert failed_filter_response.status_code == 200
    failed_filter_body = failed_filter_response.json()
    assert failed_filter_body["total"] == 1
    assert failed_filter_body["items"][0]["id"] == failed_execution_id
    assert failed_filter_body["items"][0]["status"] == "failed"

    assert workflow_filter_response.status_code == 200
    workflow_filter_body = workflow_filter_response.json()
    assert workflow_filter_body["total"] == 1
    assert workflow_filter_body["items"][0]["workflow_id"] == success_workflow_id

    assert event_type_filter_response.status_code == 200
    event_type_filter_body = event_type_filter_response.json()
    assert event_type_filter_body["total"] == 1
    assert event_type_filter_body["items"][0]["id"] == failed_execution_id

    assert pagination_response.status_code == 200
    pagination_body = pagination_response.json()
    assert pagination_body["total"] == 2
    assert pagination_body["page"] == 2
    assert pagination_body["page_size"] == 1
    assert len(pagination_body["items"]) == 1

    assert failed_workflow_id != success_workflow_id


def test_list_executions_rejects_blank_event_type_filter(client: TestClient) -> None:
    headers = authenticate_user(client, email="owner@example.com")

    response = client.get("/api/v1/executions?event_type=%20%20", headers=headers)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_execution_filter"


def test_get_execution_detail_returns_steps_in_execution_order(client: TestClient) -> None:
    headers = authenticate_user(client, email="owner@example.com")
    workflow_id = create_workflow(client, headers, event_type="user_registered")
    transform_step_id = add_step(
        client,
        headers,
        workflow_id=workflow_id,
        step_order=1,
        step_type="transform_payload",
        step_config={"set_fields": {"source": "traceflow"}},
    )
    mark_success_step_id = add_step(
        client,
        headers,
        workflow_id=workflow_id,
        step_order=2,
        step_type="mark_success",
        step_config={},
    )
    execute_response = client.post(
        "/api/v1/events",
        headers=headers,
        json={"event_type": "user_registered", "payload": {"email": "user@example.com"}},
    )
    execution_id = execute_response.json()["execution_id"]

    response = client.get(f"/api/v1/executions/{execution_id}", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == execution_id
    assert body["status"] == "success"
    assert [step["workflow_step_id"] for step in body["steps"]] == [
        transform_step_id,
        mark_success_step_id,
    ]
    assert body["steps"][0]["output_data"]["payload"]["source"] == "traceflow"
    assert body["steps"][1]["input_data"]["source"] == "traceflow"


def test_get_execution_detail_forbidden_for_other_user(client: TestClient) -> None:
    owner_headers = authenticate_user(client, email="owner@example.com")
    other_headers = authenticate_user(client, email="other@example.com")
    _, execution_id = create_success_execution(
        client,
        owner_headers,
        event_type="user_registered",
    )

    response = client.get(f"/api/v1/executions/{execution_id}", headers=other_headers)

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "forbidden_resource_access"


def test_get_execution_detail_returns_not_found_for_unknown_execution(
    client: TestClient,
) -> None:
    headers = authenticate_user(client, email="owner@example.com")

    response = client.get("/api/v1/executions/missing-execution", headers=headers)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "execution_not_found"
