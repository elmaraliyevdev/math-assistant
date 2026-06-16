"""Organization management API tests."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from tests.api.auth_helpers import register_and_auth, register_user


def test_get_organization(api_client: TestClient) -> None:
    auth = register_and_auth(api_client, email="get-org@example.com")
    response = api_client.get(
        f"/organizations/{auth['organization_id']}",
        headers=auth["headers"],
    )
    assert response.status_code == 200
    assert response.json()["id"] == auth["organization_id"]


def test_get_organization_not_member(api_client: TestClient) -> None:
    owner = register_and_auth(api_client, email="org-owner@example.com")
    outsider = register_and_auth(api_client, email="org-outsider@example.com")
    response = api_client.get(
        f"/organizations/{owner['organization_id']}",
        headers=outsider["headers"],
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "ORGANIZATION_ACCESS_DENIED"


def test_get_organization_not_found(
    api_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = api_client.get(
        f"/organizations/{uuid.uuid4()}",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_update_organization(api_client: TestClient) -> None:
    auth = register_and_auth(api_client, email="update-org@example.com")
    response = api_client.patch(
        f"/organizations/{auth['organization_id']}",
        json={"name": "Renamed Studio", "slug": "renamed-studio"},
        headers=auth["headers"],
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Renamed Studio"
    assert body["slug"] == "renamed-studio"


def test_update_organization_forbidden_for_viewer(api_client: TestClient) -> None:
    owner = register_and_auth(api_client, email="update-owner@example.com")
    viewer = register_and_auth(api_client, email="update-viewer@example.com")
    api_client.post(
        f"/organizations/{owner['organization_id']}/members",
        json={"userId": viewer["user"]["id"], "role": "viewer"},
        headers=owner["headers"],
    )
    response = api_client.patch(
        f"/organizations/{owner['organization_id']}",
        json={"name": "Should Fail"},
        headers=viewer["headers"],
    )
    assert response.status_code == 403


def test_duplicate_organization_slug(api_client: TestClient) -> None:
    auth = register_and_auth(api_client, email="dup-slug@example.com")
    first = api_client.post(
        "/organizations",
        json={"name": "First Studio", "slug": "shared-slug"},
        headers=auth["headers"],
    )
    assert first.status_code == 201
    duplicate = api_client.post(
        "/organizations",
        json={"name": "Second Studio", "slug": "shared-slug"},
        headers=auth["headers"],
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "DUPLICATE_ORGANIZATION_SLUG"


def test_add_member_updates_existing_role(api_client: TestClient) -> None:
    owner = register_and_auth(api_client, email="role-owner@example.com")
    member = register_and_auth(api_client, email="role-member@example.com")
    org_id = owner["organization_id"]
    api_client.post(
        f"/organizations/{org_id}/members",
        json={"userId": member["user"]["id"], "role": "viewer"},
        headers=owner["headers"],
    )
    updated = api_client.post(
        f"/organizations/{org_id}/members",
        json={"userId": member["user"]["id"], "role": "developer"},
        headers=owner["headers"],
    )
    assert updated.status_code == 201
    assert updated.json()["role"] == "developer"


def test_add_member_user_not_found(api_client: TestClient) -> None:
    auth = register_and_auth(api_client, email="missing-user@example.com")
    response = api_client.post(
        f"/organizations/{auth['organization_id']}/members",
        json={"userId": str(uuid.uuid4()), "role": "developer"},
        headers=auth["headers"],
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "USER_NOT_FOUND"


def test_add_owner_role_rejected(api_client: TestClient) -> None:
    owner = register_and_auth(api_client, email="owner-role@example.com")
    member = register_user(api_client, email="owner-target@example.com")
    response = api_client.post(
        f"/organizations/{owner['organization_id']}/members",
        json={"userId": member["user"]["id"], "role": "owner"},
        headers=owner["headers"],
    )
    assert response.status_code == 403


def test_remove_member_not_found(api_client: TestClient) -> None:
    owner = register_and_auth(api_client, email="remove-missing@example.com")
    response = api_client.delete(
        f"/organizations/{owner['organization_id']}/members/{uuid.uuid4()}",
        headers=owner["headers"],
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "MEMBER_NOT_FOUND"


def test_cannot_remove_organization_owner(api_client: TestClient) -> None:
    owner = register_and_auth(api_client, email="protect-owner@example.com")
    response = api_client.delete(
        f"/organizations/{owner['organization_id']}/members/{owner['user']['id']}",
        headers=owner["headers"],
    )
    assert response.status_code == 403
