"""Distributed simulation API integration tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.api.auth_helpers import register_and_auth
from tests.api.test_simulations_api import _create_game_version, wait_for_simulation


def _run_distributed_simulation(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> str:
    game_version_id = _create_game_version(api_client, auth_context, valid_canonical_json)
    created = api_client.post(
        "/simulations",
        json={"gameVersionId": game_version_id, "spinCount": 20},
        headers=auth_context["headers"],
    )
    assert created.status_code == 202, created.text
    simulation_id = created.json()["simulationId"]
    wait_for_simulation(api_client, simulation_id, headers=auth_context["headers"])
    return simulation_id


def test_distributed_simulation_flow(
    distributed_api_client: TestClient,
    valid_canonical_json: dict,
) -> None:
    auth_context = register_and_auth(distributed_api_client)
    simulation_id = _run_distributed_simulation(
        distributed_api_client,
        auth_context,
        valid_canonical_json,
    )
    headers = auth_context["headers"]

    detail = distributed_api_client.get(f"/simulations/{simulation_id}", headers=headers)
    assert detail.status_code == 200
    body = detail.json()
    assert body["status"] == "completed"
    assert body["distributedExecution"] is True
    assert body["totalShards"] > 0

    shards = distributed_api_client.get(
        f"/simulations/{simulation_id}/shards",
        headers=headers,
    )
    assert shards.status_code == 200
    assert len(shards.json()["items"]) == body["totalShards"]

    queue = distributed_api_client.get("/simulations/queue", headers=headers)
    assert queue.status_code == 200

    workers = distributed_api_client.get("/workers", headers=headers)
    assert workers.status_code == 200

    health = distributed_api_client.get("/workers/health", headers=headers)
    assert health.status_code == 200


def test_distributed_cancel(
    distributed_api_client: TestClient,
    valid_canonical_json: dict,
) -> None:
    auth_context = register_and_auth(distributed_api_client)
    game_version_id = _create_game_version(
        distributed_api_client,
        auth_context,
        valid_canonical_json,
    )
    created = distributed_api_client.post(
        "/simulations",
        json={"gameVersionId": game_version_id, "spinCount": 20},
        headers=auth_context["headers"],
    )
    assert created.status_code == 202
    simulation_id = created.json()["simulationId"]
    cancelled = distributed_api_client.post(
        f"/simulations/{simulation_id}/cancel",
        headers=auth_context["headers"],
    )
    assert cancelled.status_code in {202, 409}
