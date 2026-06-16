"""Game management API tests."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient


def _create_game(
    client: TestClient,
    headers: dict[str, str],
    organization_id: str,
    *,
    name: str,
    description: str | None = None,
) -> dict:
    payload: dict[str, str] = {
        "name": name,
        "organizationId": organization_id,
    }
    if description is not None:
        payload["description"] = description
    response = client.post("/games", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


def test_create_game(api_client: TestClient, auth_context: dict) -> None:
    body = _create_game(
        api_client,
        auth_context["headers"],
        auth_context["organization_id"],
        name="Book of Fortune",
        description="5x3 video slot with Free Spins and Hold & Win",
    )
    assert body["name"] == "Book of Fortune"
    assert body["description"] == "5x3 video slot with Free Spins and Hold & Win"
    assert body["organizationId"] == auth_context["organization_id"]
    assert "id" in body


def test_get_game_requires_auth(api_client: TestClient) -> None:
    response = api_client.get(f"/games/{uuid.uuid4()}")
    assert response.status_code == 401


def test_get_game(api_client: TestClient, auth_context: dict) -> None:
    created = _create_game(
        api_client,
        auth_context["headers"],
        auth_context["organization_id"],
        name="Lookup Game",
    )
    response = api_client.get(
        f"/games/{created['id']}",
        headers=auth_context["headers"],
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Lookup Game"


def test_get_game_not_found(api_client: TestClient, auth_headers: dict[str, str]) -> None:
    response = api_client.get(f"/games/{uuid.uuid4()}", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "GAME_NOT_FOUND"


def test_list_games_pagination_and_search(
    api_client: TestClient,
    auth_context: dict,
) -> None:
    headers = auth_context["headers"]
    org_id = auth_context["organization_id"]
    _create_game(api_client, headers, org_id, name="Alpha Slot")
    _create_game(api_client, headers, org_id, name="Beta Slot")
    _create_game(api_client, headers, org_id, name="Alpha Deluxe")

    page_one = api_client.get("/games", params={"page": 1, "pageSize": 2}, headers=headers)
    assert page_one.status_code == 200
    body = page_one.json()
    assert body["total"] == 3

    search = api_client.get("/games", params={"search": "Alpha"}, headers=headers)
    assert search.status_code == 200
    assert search.json()["total"] == 2


def test_update_game(api_client: TestClient, auth_context: dict) -> None:
    created = _create_game(
        api_client,
        auth_context["headers"],
        auth_context["organization_id"],
        name="Old Name",
        description="Old",
    )
    response = api_client.patch(
        f"/games/{created['id']}",
        json={"name": "New Name", "description": "Updated"},
        headers=auth_context["headers"],
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "New Name"
    assert body["description"] == "Updated"


def test_delete_game_returns_204(api_client: TestClient, auth_context: dict) -> None:
    created = _create_game(
        api_client,
        auth_context["headers"],
        auth_context["organization_id"],
        name="Delete Me",
    )
    response = api_client.delete(
        f"/games/{created['id']}",
        headers=auth_context["headers"],
    )
    assert response.status_code == 204
    assert api_client.get(
        f"/games/{created['id']}",
        headers=auth_context["headers"],
    ).status_code == 404


def test_create_game_propagates_request_id(
    api_client: TestClient,
    auth_context: dict,
) -> None:
    response = api_client.post(
        "/games",
        json={
            "name": "Request ID Game",
            "organizationId": auth_context["organization_id"],
        },
        headers={**auth_context["headers"], "X-Request-Id": "game-create-req-1"},
    )
    assert response.status_code == 201
    assert response.headers["X-Request-Id"] == "game-create-req-1"
