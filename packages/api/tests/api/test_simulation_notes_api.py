"""Simulation notes API tests."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from tests.api.test_simulations_api import (
    _create_game_version,
    wait_for_simulation,
)


def _completed_simulation(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> str:
    game_version_id = _create_game_version(api_client, auth_context, valid_canonical_json)
    created = api_client.post(
        "/simulations",
        json={"gameVersionId": game_version_id, "spinCount": 5},
        headers=auth_context["headers"],
    ).json()
    wait_for_simulation(
        api_client,
        created["simulationId"],
        headers=auth_context["headers"],
    )
    return created["simulationId"]


def test_simulation_notes_crud(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    simulation_id = _completed_simulation(api_client, auth_context, valid_canonical_json)
    create = api_client.post(
        f"/simulations/{simulation_id}/notes",
        json={"content": "Reduced scatter frequency from 68% to 35%."},
        headers=auth_context["headers"],
    )
    assert create.status_code == 201
    note = create.json()
    assert note["content"].startswith("Reduced scatter")
    assert note["simulationId"] == simulation_id

    listed = api_client.get(
        f"/simulations/{simulation_id}/notes",
        headers=auth_context["headers"],
    )
    assert listed.status_code == 200
    assert len(listed.json()["items"]) == 1

    deleted = api_client.delete(
        f"/simulations/{simulation_id}/notes/{note['id']}",
        headers=auth_context["headers"],
    )
    assert deleted.status_code == 204

    listed_after = api_client.get(
        f"/simulations/{simulation_id}/notes",
        headers=auth_context["headers"],
    )
    assert listed_after.json()["items"] == []


def test_simulation_note_not_found(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    simulation_id = _completed_simulation(api_client, auth_context, valid_canonical_json)
    response = api_client.delete(
        f"/simulations/{simulation_id}/notes/{uuid.uuid4()}",
        headers=auth_context["headers"],
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "SIMULATION_NOTE_NOT_FOUND"
