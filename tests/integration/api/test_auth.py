from __future__ import annotations

from fastapi.testclient import TestClient


def test_register_user_returns_created_user(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "StrongPass123"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "user@example.com"
    assert body["is_active"] is True
    assert "created_at" in body
    assert "hashed_password" not in body


def test_register_user_rejects_duplicate_email(client: TestClient) -> None:
    payload = {"email": "user@example.com", "password": "StrongPass123"}

    first_response = client.post("/api/v1/auth/register", json=payload)
    second_response = client.post("/api/v1/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["error"]["code"] == "email_already_exists"


def test_login_user_returns_access_token(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "StrongPass123"},
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "StrongPass123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert body["access_token"]


def test_login_user_rejects_invalid_credentials(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "StrongPass123"},
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "wrong-pass"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"


def test_get_current_user_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "authentication_required"


def test_get_current_user_returns_authenticated_user(client: TestClient) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "StrongPass123"},
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "StrongPass123"},
    )
    access_token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert register_response.status_code == 201
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"
