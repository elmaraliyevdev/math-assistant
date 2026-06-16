"""Mathematics API integration tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.api.test_simulations_api import _create_game_version


def test_theoretical_analysis(api_client: TestClient, auth_context: dict, valid_canonical_json: dict) -> None:
    game_version_id = _create_game_version(api_client, auth_context, valid_canonical_json)
    response = api_client.post(
        "/mathematics/theoretical",
        json={"gameVersionId": game_version_id},
        headers=auth_context["headers"],
    )
    assert response.status_code == 200
    body = response.json()
    assert body["rtp"]["totalRtp"] > 0
    assert body["rtp"]["outcomeCount"] == 3125
    assert any(item["trigger"] == "FREE_SPINS" for item in body["featureProbabilities"])


def test_calibrate_mathematics(api_client: TestClient, auth_context: dict, valid_canonical_json: dict) -> None:
    game_version_id = _create_game_version(api_client, auth_context, valid_canonical_json)
    response = api_client.post(
        "/mathematics/calibrate",
        json={
            "gameVersionId": game_version_id,
            "simulatedRtp": 0.0512,
        },
        headers=auth_context["headers"],
    )
    assert response.status_code == 200
    body = response.json()
    assert body["calibration"]["theoreticalRtp"] > 0
    assert body["discrepancy"]["items"]
    assert isinstance(body["recommendations"], list)


def test_certification_report_json_download(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game_version_id = _create_game_version(api_client, auth_context, valid_canonical_json)
    preview = api_client.post(
        "/mathematics/certification-report",
        json={"gameVersionId": game_version_id},
        headers=auth_context["headers"],
    )
    assert preview.status_code == 200
    assert preview.json()["gameTitle"]

    download = api_client.post(
        "/mathematics/certification-report",
        json={"gameVersionId": game_version_id, "format": "json"},
        headers=auth_context["headers"],
    )
    assert download.status_code == 200
    assert download.headers["content-type"].startswith("application/json")
    assert b"gameTitle" in download.content
