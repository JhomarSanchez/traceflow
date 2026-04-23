from __future__ import annotations

from fastapi.testclient import TestClient


def authenticate_user(
    client: TestClient,
    *,
    email: str,
    password: str = "StrongPass123",
) -> dict[str, str]:
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    access_token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


def test_create_workflow_returns_created_workflow(client: TestClient) -> None:
    headers = authenticate_user(client, email="owner@example.com")

    response = client.post(
        "/api/v1/workflows",
        headers=headers,
        json={
            "name": "User registration workflow",
            "description": "Processes user registrations",
            "event_type": "user_registered",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "User registration workflow"
    assert body["event_type"] == "user_registered"
    assert body["is_active"] is True
    assert body["owner_id"]


def test_create_workflow_rejects_second_active_workflow_for_same_event_type(
    client: TestClient,
) -> None:
    headers = authenticate_user(client, email="owner@example.com")
    payload = {
        "name": "User registration workflow",
        "description": "Processes user registrations",
        "event_type": "user_registered",
    }

    first_response = client.post("/api/v1/workflows", headers=headers, json=payload)
    second_response = client.post(
        "/api/v1/workflows",
        headers=headers,
        json={**payload, "name": "Another workflow"},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["error"]["code"] == "active_workflow_conflict"


def test_list_workflows_returns_only_current_user_workflows(client: TestClient) -> None:
    owner_headers = authenticate_user(client, email="owner@example.com")
    other_headers = authenticate_user(client, email="other@example.com")

    client.post(
        "/api/v1/workflows",
        headers=owner_headers,
        json={"name": "Owner workflow", "description": None, "event_type": "user_registered"},
    )
    client.post(
        "/api/v1/workflows",
        headers=other_headers,
        json={"name": "Other workflow", "description": None, "event_type": "order_created"},
    )

    response = client.get("/api/v1/workflows", headers=owner_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["name"] == "Owner workflow"


def test_list_workflows_rejects_blank_event_type_filter(client: TestClient) -> None:
    headers = authenticate_user(client, email="owner@example.com")

    response = client.get("/api/v1/workflows?event_type=%20%20%20", headers=headers)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_workflow_data"


def test_get_workflow_detail_forbidden_for_other_user(client: TestClient) -> None:
    owner_headers = authenticate_user(client, email="owner@example.com")
    other_headers = authenticate_user(client, email="other@example.com")

    create_response = client.post(
        "/api/v1/workflows",
        headers=owner_headers,
        json={"name": "Owner workflow", "description": None, "event_type": "user_registered"},
    )
    workflow_id = create_response.json()["id"]

    response = client.get(f"/api/v1/workflows/{workflow_id}", headers=other_headers)

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "forbidden_resource_access"


def test_update_workflow_persists_changes(client: TestClient) -> None:
    headers = authenticate_user(client, email="owner@example.com")
    create_response = client.post(
        "/api/v1/workflows",
        headers=headers,
        json={"name": "Old workflow", "description": None, "event_type": "user_registered"},
    )
    workflow_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/workflows/{workflow_id}",
        headers=headers,
        json={
            "name": "Updated workflow",
            "description": "Updated description",
            "event_type": "account_created",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Updated workflow"
    assert body["description"] == "Updated description"
    assert body["event_type"] == "account_created"


def test_update_workflow_rejects_conflicting_active_event_type(client: TestClient) -> None:
    headers = authenticate_user(client, email="owner@example.com")
    first_workflow_response = client.post(
        "/api/v1/workflows",
        headers=headers,
        json={"name": "First workflow", "description": None, "event_type": "user_registered"},
    )
    second_workflow_response = client.post(
        "/api/v1/workflows",
        headers=headers,
        json={"name": "Second workflow", "description": None, "event_type": "order_created"},
    )
    update_response = client.patch(
        f"/api/v1/workflows/{second_workflow_response.json()['id']}",
        headers=headers,
        json={"event_type": "user_registered"},
    )

    assert first_workflow_response.status_code == 201
    assert second_workflow_response.status_code == 201
    assert update_response.status_code == 409
    assert update_response.json()["error"]["code"] == "active_workflow_conflict"


def test_activate_and_deactivate_workflow_toggle_state(client: TestClient) -> None:
    headers = authenticate_user(client, email="owner@example.com")
    create_response = client.post(
        "/api/v1/workflows",
        headers=headers,
        json={"name": "Toggle workflow", "description": None, "event_type": "user_registered"},
    )
    workflow_id = create_response.json()["id"]

    deactivate_response = client.post(
        f"/api/v1/workflows/{workflow_id}/deactivate",
        headers=headers,
    )
    activate_response = client.post(
        f"/api/v1/workflows/{workflow_id}/activate",
        headers=headers,
    )
    detail_response = client.get(f"/api/v1/workflows/{workflow_id}", headers=headers)

    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False
    assert activate_response.status_code == 200
    assert activate_response.json()["is_active"] is True
    assert detail_response.json()["is_active"] is True


def test_activate_workflow_rejects_conflicting_active_event_type(client: TestClient) -> None:
    headers = authenticate_user(client, email="owner@example.com")
    first_workflow_response = client.post(
        "/api/v1/workflows",
        headers=headers,
        json={"name": "First workflow", "description": None, "event_type": "user_registered"},
    )
    second_workflow_response = client.post(
        "/api/v1/workflows",
        headers=headers,
        json={"name": "Second workflow", "description": None, "event_type": "order_created"},
    )

    deactivate_second_response = client.post(
        f"/api/v1/workflows/{second_workflow_response.json()['id']}/deactivate",
        headers=headers,
    )
    update_second_response = client.patch(
        f"/api/v1/workflows/{second_workflow_response.json()['id']}",
        headers=headers,
        json={"event_type": "user_registered"},
    )
    activate_response = client.post(
        f"/api/v1/workflows/{second_workflow_response.json()['id']}/activate",
        headers=headers,
    )

    assert first_workflow_response.status_code == 201
    assert deactivate_second_response.status_code == 200
    assert update_second_response.status_code == 200
    assert activate_response.status_code == 409
    assert activate_response.json()["error"]["code"] == "active_workflow_conflict"
