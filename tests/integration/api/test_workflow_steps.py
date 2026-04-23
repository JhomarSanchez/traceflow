from __future__ import annotations

from fastapi.testclient import TestClient

from tests.integration.api.test_workflows import authenticate_user


def create_workflow(client: TestClient, headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/workflows",
        headers=headers,
        json={"name": "Workflow", "description": None, "event_type": "user_registered"},
    )
    return response.json()["id"]


def test_add_workflow_step_returns_created_step(client: TestClient) -> None:
    headers = authenticate_user(client, email="owner@example.com")
    workflow_id = create_workflow(client, headers)

    response = client.post(
        f"/api/v1/workflows/{workflow_id}/steps",
        headers=headers,
        json={
            "step_order": 1,
            "step_type": "log_message",
            "step_config": {"message": "hello"},
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["workflow_id"] == workflow_id
    assert body["step_order"] == 1
    assert body["step_type"] == "log_message"
    assert body["step_config"] == {"message": "hello"}


def test_list_workflow_steps_returns_items_in_step_order(client: TestClient) -> None:
    headers = authenticate_user(client, email="owner@example.com")
    workflow_id = create_workflow(client, headers)

    client.post(
        f"/api/v1/workflows/{workflow_id}/steps",
        headers=headers,
        json={"step_order": 2, "step_type": "mark_success", "step_config": {}},
    )
    client.post(
        f"/api/v1/workflows/{workflow_id}/steps",
        headers=headers,
        json={
            "step_order": 1,
            "step_type": "log_message",
            "step_config": {"message": "first"},
        },
    )

    response = client.get(f"/api/v1/workflows/{workflow_id}/steps", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert [item["step_order"] for item in body["items"]] == [1, 2]
    assert [item["step_type"] for item in body["items"]] == [
        "log_message",
        "mark_success",
    ]


def test_add_workflow_step_rejects_duplicate_step_order(client: TestClient) -> None:
    headers = authenticate_user(client, email="owner@example.com")
    workflow_id = create_workflow(client, headers)

    first_response = client.post(
        f"/api/v1/workflows/{workflow_id}/steps",
        headers=headers,
        json={"step_order": 1, "step_type": "persist_payload", "step_config": {}},
    )
    second_response = client.post(
        f"/api/v1/workflows/{workflow_id}/steps",
        headers=headers,
        json={"step_order": 1, "step_type": "mark_success", "step_config": {}},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["error"]["code"] == "step_order_conflict"


def test_add_workflow_step_forbidden_for_other_user(client: TestClient) -> None:
    owner_headers = authenticate_user(client, email="owner@example.com")
    other_headers = authenticate_user(client, email="other@example.com")
    workflow_id = create_workflow(client, owner_headers)

    response = client.post(
        f"/api/v1/workflows/{workflow_id}/steps",
        headers=other_headers,
        json={"step_order": 1, "step_type": "mark_success", "step_config": {}},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "forbidden_resource_access"


def test_list_workflow_steps_forbidden_for_other_user(client: TestClient) -> None:
    owner_headers = authenticate_user(client, email="owner@example.com")
    other_headers = authenticate_user(client, email="other@example.com")
    workflow_id = create_workflow(client, owner_headers)

    response = client.get(f"/api/v1/workflows/{workflow_id}/steps", headers=other_headers)

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "forbidden_resource_access"


def test_remove_workflow_step_deletes_step(client: TestClient) -> None:
    headers = authenticate_user(client, email="owner@example.com")
    workflow_id = create_workflow(client, headers)
    create_step_response = client.post(
        f"/api/v1/workflows/{workflow_id}/steps",
        headers=headers,
        json={"step_order": 1, "step_type": "mark_success", "step_config": {}},
    )
    step_id = create_step_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/workflows/{workflow_id}/steps/{step_id}",
        headers=headers,
    )
    list_response = client.get(f"/api/v1/workflows/{workflow_id}/steps", headers=headers)

    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert list_response.json()["items"] == []


def test_remove_workflow_step_returns_not_found_for_unknown_step(client: TestClient) -> None:
    headers = authenticate_user(client, email="owner@example.com")
    workflow_id = create_workflow(client, headers)

    response = client.delete(
        f"/api/v1/workflows/{workflow_id}/steps/missing-step",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "workflow_step_not_found"


def test_remove_workflow_step_forbidden_for_other_user(client: TestClient) -> None:
    owner_headers = authenticate_user(client, email="owner@example.com")
    other_headers = authenticate_user(client, email="other@example.com")
    workflow_id = create_workflow(client, owner_headers)
    create_step_response = client.post(
        f"/api/v1/workflows/{workflow_id}/steps",
        headers=owner_headers,
        json={"step_order": 1, "step_type": "mark_success", "step_config": {}},
    )
    step_id = create_step_response.json()["id"]

    response = client.delete(
        f"/api/v1/workflows/{workflow_id}/steps/{step_id}",
        headers=other_headers,
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "forbidden_resource_access"


def test_add_workflow_step_rejects_invalid_step_type(client: TestClient) -> None:
    headers = authenticate_user(client, email="owner@example.com")
    workflow_id = create_workflow(client, headers)

    response = client.post(
        f"/api/v1/workflows/{workflow_id}/steps",
        headers=headers,
        json={"step_order": 1, "step_type": "send_email", "step_config": {}},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_add_workflow_step_rejects_non_object_step_config(client: TestClient) -> None:
    headers = authenticate_user(client, email="owner@example.com")
    workflow_id = create_workflow(client, headers)

    response = client.post(
        f"/api/v1/workflows/{workflow_id}/steps",
        headers=headers,
        json={"step_order": 1, "step_type": "mark_success", "step_config": None},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
