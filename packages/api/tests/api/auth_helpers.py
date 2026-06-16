"""Authentication helpers for API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient


def register_user(
    client: TestClient,
    *,
    email: str = "developer@example.com",
    password: str = "secure-password",
    full_name: str = "Test Developer",
) -> dict:
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "fullName": full_name,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def register_and_auth(
    client: TestClient,
    *,
    email: str = "developer@example.com",
    password: str = "secure-password",
    full_name: str = "Test Developer",
) -> dict:
    body = register_user(
        client,
        email=email,
        password=password,
        full_name=full_name,
    )
    return {
        "headers": auth_headers(body["tokens"]["accessToken"]),
        "organization_id": body["organizationId"],
        "user": body["user"],
        "tokens": body["tokens"],
    }
