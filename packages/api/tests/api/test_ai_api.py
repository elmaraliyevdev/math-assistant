"""AI Mathematics Assistant API integration tests."""

from __future__ import annotations

from tests.api.test_simulation_compare_api import _create_completed_simulation
from tests.api.test_simulations_api import _create_game_version


def test_analyze_simulation(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    simulation_id = _create_completed_simulation(
        api_client,
        auth_context,
        valid_canonical_json,
        rtp=0.51,
    )
    response = api_client.post(
        f"/ai/simulations/{simulation_id}/analyze",
        headers=auth_context["headers"],
    )
    assert response.status_code == 200
    body = response.json()
    assert body["simulationId"] == simulation_id
    assert body["content"]
    assert body["citations"]
    assert any("simulation_results" in item["source"] for item in body["citations"])


def test_recommend_simulation(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    simulation_id = _create_completed_simulation(
        api_client,
        auth_context,
        valid_canonical_json,
        rtp=0.51,
    )
    response = api_client.post(
        f"/ai/simulations/{simulation_id}/recommend",
        json={"targetRtp": 96.0},
        headers=auth_context["headers"],
    )
    assert response.status_code == 200
    body = response.json()
    assert body["targetRtp"] == 96.0
    assert isinstance(body["recommendations"], list)
    assert body["citations"]


def test_compare_simulations_assistant(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game_version_id = _create_game_version(api_client, auth_context, valid_canonical_json)
    sim_a = _create_completed_simulation(
        api_client,
        auth_context,
        valid_canonical_json,
        rtp=0.51,
        game_version_id=game_version_id,
    )
    sim_b = _create_completed_simulation(
        api_client,
        auth_context,
        valid_canonical_json,
        rtp=0.62,
        game_version_id=game_version_id,
    )
    response = api_client.post(
        "/ai/simulations/compare",
        json={"simulationIds": [sim_a, sim_b]},
        headers=auth_context["headers"],
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["simulationIds"]) == 2
    assert "RTP" in body["content"]


def test_explain_game_version(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game_version_id = _create_game_version(api_client, auth_context, valid_canonical_json)
    response = api_client.post(
        f"/ai/game-versions/{game_version_id}/explain",
        headers=auth_context["headers"],
    )
    assert response.status_code == 200
    body = response.json()
    assert body["gameVersionId"] == game_version_id
    assert body["citations"]
    assert any(
        citation["source"] in {"game_canonical_json", "theoretical_analysis"}
        for citation in body["citations"]
    )
