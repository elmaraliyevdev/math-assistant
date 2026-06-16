"""Authentication API tests."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from tests.api.auth_helpers import auth_headers, register_and_auth, register_user


def test_register_login_and_me(api_client: TestClient) -> None:
    registered = register_user(
        api_client,
        email="alice@example.com",
        full_name="Alice Example",
    )
    assert registered["user"]["email"] == "alice@example.com"
    assert "organizationId" in registered

    login = api_client.post(
        "/auth/login",
        json={"email": "alice@example.com", "password": "secure-password"},
    )
    assert login.status_code == 200
    tokens = login.json()
    assert tokens["tokenType"] == "bearer"
    assert tokens["expiresIn"] == 15 * 60

    me = api_client.get("/auth/me", headers=auth_headers(tokens["accessToken"]))
    assert me.status_code == 200
    body = me.json()
    assert body["user"]["email"] == "alice@example.com"
    assert len(body["organizations"]) == 1


def test_refresh_and_logout(api_client: TestClient) -> None:
    auth = register_and_auth(api_client, email="refresh@example.com")
    refresh = api_client.post(
        "/auth/refresh",
        json={"refreshToken": auth["tokens"]["refreshToken"]},
    )
    assert refresh.status_code == 200
    new_tokens = refresh.json()
    assert "accessToken" in new_tokens

    logout = api_client.post(
        "/auth/logout",
        json={"refreshToken": new_tokens["refreshToken"]},
    )
    assert logout.status_code == 204

    expired_refresh = api_client.post(
        "/auth/refresh",
        json={"refreshToken": new_tokens["refreshToken"]},
    )
    assert expired_refresh.status_code == 401


def test_duplicate_registration_rejected(api_client: TestClient) -> None:
    register_user(api_client, email="dup@example.com")
    response = api_client.post(
        "/auth/register",
        json={
            "email": "dup@example.com",
            "password": "secure-password",
            "fullName": "Duplicate",
        },
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "DUPLICATE_EMAIL"


def test_invalid_login_rejected(api_client: TestClient) -> None:
    register_user(api_client, email="login@example.com")
    response = api_client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_organization_isolation(api_client: TestClient) -> None:
    user_a = register_and_auth(api_client, email="user-a@example.com")
    user_b = register_and_auth(api_client, email="user-b@example.com")

    created = api_client.post(
        "/games",
        json={
            "name": "Private Game",
            "organizationId": user_a["organization_id"],
        },
        headers=user_a["headers"],
    ).json()

    forbidden = api_client.get(
        f"/games/{created['id']}",
        headers=user_b["headers"],
    )
    assert forbidden.status_code == 404


def test_organization_member_role_enforcement(api_client: TestClient) -> None:
    owner = register_and_auth(api_client, email="owner@example.com")
    viewer = register_and_auth(api_client, email="viewer@example.com")

    api_client.post(
        f"/organizations/{owner['organization_id']}/members",
        json={"userId": viewer["user"]["id"], "role": "viewer"},
        headers=owner["headers"],
    )

    create_denied = api_client.post(
        "/games",
        json={
            "name": "Viewer Cannot Create",
            "organizationId": owner["organization_id"],
        },
        headers=viewer["headers"],
    )
    assert create_denied.status_code == 403


def test_personal_workspace_created_on_register(api_client: TestClient) -> None:
    auth = register_and_auth(api_client, email="workspace@example.com", full_name="Workspace User")
    orgs = api_client.get("/organizations", headers=auth["headers"])
    assert orgs.status_code == 200
    items = orgs.json()["items"]
    assert len(items) == 1
    assert items[0]["name"] == "Workspace User's Workspace"


def test_create_organization(api_client: TestClient, auth_headers: dict[str, str]) -> None:
    response = api_client.post(
        "/organizations",
        json={"name": "Studio Team", "slug": "studio-team"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["slug"] == "studio-team"


def test_remove_organization_member(api_client: TestClient) -> None:
    owner = register_and_auth(api_client, email="remove-owner@example.com")
    member = register_and_auth(api_client, email="remove-member@example.com")
    api_client.post(
        f"/organizations/{owner['organization_id']}/members",
        json={"userId": member["user"]["id"], "role": "developer"},
        headers=owner["headers"],
    )
    removed = api_client.delete(
        f"/organizations/{owner['organization_id']}/members/{member['user']['id']}",
        headers=owner["headers"],
    )
    assert removed.status_code == 204


def test_invalid_token_rejected(api_client: TestClient) -> None:
    response = api_client.get(
        "/auth/me",
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert response.status_code == 401


def test_missing_auth_header_rejected(api_client: TestClient) -> None:
    response = api_client.get("/auth/me")
    assert response.status_code == 401


def test_invalid_refresh_token_rejected(api_client: TestClient) -> None:
    response = api_client.post(
        "/auth/refresh",
        json={"refreshToken": "not-a-valid-token"},
    )
    assert response.status_code == 401
