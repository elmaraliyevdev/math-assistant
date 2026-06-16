"""Game version management API tests."""

from __future__ import annotations

import copy
import uuid

from fastapi.testclient import TestClient


def _create_game(client: TestClient, auth_context: dict) -> str:
    response = client.post(
        "/games",
        json={
            "name": "Version Host Game",
            "description": "Host",
            "organizationId": auth_context["organization_id"],
        },
        headers=auth_context["headers"],
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_create_version_from_fixture(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game_id = _create_game(api_client, auth_context)
    response = api_client.post(
        f"/games/{game_id}/versions",
        json={
            "canonicalJson": valid_canonical_json,
            "engineVersion": "runtime-core@1.8.0",
        },
        headers=auth_context["headers"],
    )
    assert response.status_code == 201
    body = response.json()
    assert body["version"] == 1
    assert len(body["contentHash"]) == 64
    assert body["engineVersion"] == "runtime-core@1.8.0"
    assert body["validationSummary"]["passed"] is True
    assert body["validationSummary"]["findingCount"] == 0
    assert body["validationSummary"]["findings"] == []


def test_create_version_auto_increments(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game_id = _create_game(api_client, auth_context)
    first_json = copy.deepcopy(valid_canonical_json)
    second_json = copy.deepcopy(valid_canonical_json)
    second_json["metadata"] = copy.deepcopy(valid_canonical_json["metadata"])
    second_json["metadata"]["title"] = "Modified Title"

    first = api_client.post(
        f"/games/{game_id}/versions",
        json={"canonicalJson": first_json, "engineVersion": "runtime-core@1.8.0"},
        headers=auth_context["headers"],
    )
    second = api_client.post(
        f"/games/{game_id}/versions",
        json={"canonicalJson": second_json, "engineVersion": "runtime-core@1.8.0"},
        headers=auth_context["headers"],
    )
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["version"] == 1
    assert second.json()["version"] == 2


def test_duplicate_content_hash_conflict(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game_id = _create_game(api_client, auth_context)
    payload = {
        "canonicalJson": valid_canonical_json,
        "engineVersion": "runtime-core@1.8.0",
    }
    first = api_client.post(
        f"/games/{game_id}/versions",
        json=payload,
        headers=auth_context["headers"],
    )
    duplicate = api_client.post(
        f"/games/{game_id}/versions",
        json=payload,
        headers=auth_context["headers"],
    )
    assert first.status_code == 201
    assert duplicate.status_code == 409
    body = duplicate.json()
    assert body["error"]["code"] == "DUPLICATE_GAME_VERSION"
    assert body["error"]["details"]["contentHash"] == first.json()["contentHash"]


def test_validation_failure(
    api_client: TestClient,
    auth_context: dict,
    invalid_canonical_json: dict,
) -> None:
    game_id = _create_game(api_client, auth_context)
    response = api_client.post(
        f"/games/{game_id}/versions",
        json={
            "canonicalJson": invalid_canonical_json,
            "engineVersion": "runtime-core@1.8.0",
        },
        headers=auth_context["headers"],
    )
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_FAILED"
    assert body["error"]["details"]["findings"]


def test_engine_version_mismatch(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game_id = _create_game(api_client, auth_context)
    response = api_client.post(
        f"/games/{game_id}/versions",
        json={
            "canonicalJson": valid_canonical_json,
            "engineVersion": "runtime-core@1.0.0",
        },
        headers=auth_context["headers"],
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "ENGINE_VERSION_MISMATCH"


def test_create_version_game_not_found(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    response = api_client.post(
        f"/games/{uuid.uuid4()}/versions",
        json={
            "canonicalJson": valid_canonical_json,
            "engineVersion": "runtime-core@1.8.0",
        },
        headers=auth_context["headers"],
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "GAME_NOT_FOUND"


def test_list_and_get_versions(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game_id = _create_game(api_client, auth_context)
    created = api_client.post(
        f"/games/{game_id}/versions",
        json={
            "canonicalJson": valid_canonical_json,
            "engineVersion": "runtime-core@1.8.0",
        },
        headers=auth_context["headers"],
    ).json()

    listed = api_client.get(
        f"/games/{game_id}/versions",
        headers=auth_context["headers"],
    )
    assert listed.status_code == 200
    items = listed.json()
    assert len(items) == 1
    assert items[0]["id"] == created["id"]
    assert items[0]["version"] == 1

    detail = api_client.get(
        f"/games/{game_id}/versions/{created['id']}",
        headers=auth_context["headers"],
    )
    assert detail.status_code == 200
    detail_body = detail.json()
    assert detail_body["canonicalJson"]["schemaVersion"] == "1.0.0"
    assert detail_body["contentHash"] == created["contentHash"]


def test_get_version_not_found(
    api_client: TestClient,
    auth_context: dict,
) -> None:
    game_id = _create_game(api_client, auth_context)
    response = api_client.get(
        f"/games/{game_id}/versions/{uuid.uuid4()}",
        headers=auth_context["headers"],
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "GAME_VERSION_NOT_FOUND"


def test_delete_game_cascades_versions(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game_id = _create_game(api_client, auth_context)
    version = api_client.post(
        f"/games/{game_id}/versions",
        json={
            "canonicalJson": valid_canonical_json,
            "engineVersion": "runtime-core@1.8.0",
        },
        headers=auth_context["headers"],
    ).json()
    delete_response = api_client.delete(
        f"/games/{game_id}",
        headers=auth_context["headers"],
    )
    assert delete_response.status_code == 204
    version_lookup = api_client.get(
        f"/games/{game_id}/versions/{version['id']}",
        headers=auth_context["headers"],
    )
    assert version_lookup.status_code == 404


def test_version_endpoint_propagates_request_id(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game_id = _create_game(api_client, auth_context)
    response = api_client.post(
        f"/games/{game_id}/versions",
        json={
            "canonicalJson": valid_canonical_json,
            "engineVersion": "runtime-core@1.8.0",
        },
        headers={
            **auth_context["headers"],
            "X-Request-Id": "version-create-req-1",
        },
    )
    assert response.status_code == 201
    assert response.headers["X-Request-Id"] == "version-create-req-1"
