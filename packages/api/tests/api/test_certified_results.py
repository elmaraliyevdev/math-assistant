"""Certified simulation results API fields and PDF exports."""

from __future__ import annotations

from app.certification import CERTIFICATION_NOTICE
from app.exports.pdf_reports import build_simulation_results_pdf
from tests.api.test_simulations_api import (
    _create_game_version,
    wait_for_simulation,
)


def _certified_result_keys() -> set[str]:
    return {
        "confidenceInterval",
        "winDistribution",
        "volatilityMetrics",
        "hitFrequency",
        "engineVersion",
        "gameVersionContentHash",
        "certificationNotice",
    }


def test_simulation_results_expose_certified_metrics(
    api_client,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game_version_id = _create_game_version(
        api_client,
        auth_context,
        valid_canonical_json,
    )
    create = api_client.post(
        "/simulations",
        json={
            "gameVersionId": game_version_id,
            "spinCount": 20,
            "betMinorUnits": 100,
        },
        headers=auth_context["headers"],
    )
    simulation_id = create.json()["simulationId"]
    wait_for_simulation(api_client, simulation_id, headers=auth_context["headers"])

    response = api_client.get(
        f"/simulations/{simulation_id}/results",
        headers=auth_context["headers"],
    )
    assert response.status_code == 200
    body = response.json()
    assert _certified_result_keys().issubset(body.keys())
    assert body["certificationNotice"] == CERTIFICATION_NOTICE
    assert len(body["gameVersionContentHash"]) == 64
    assert body["engineVersion"]
    assert "buckets" in body["winDistribution"]
    assert body["volatilityMetrics"]["standardDeviation"] == body["summary"]["volatility"]
    assert body["confidenceInterval"]["lowerBound"] <= body["confidenceInterval"]["rtp"]
    assert body["confidenceInterval"]["upperBound"] >= body["confidenceInterval"]["rtp"]
    assert body["exposure"]["exposureCapApplied"] in {True, False}


def test_simulation_pdf_export_is_valid_pdf(
    api_client,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game_version_id = _create_game_version(
        api_client,
        auth_context,
        valid_canonical_json,
    )
    create = api_client.post(
        "/simulations",
        json={
            "gameVersionId": game_version_id,
            "spinCount": 20,
            "betMinorUnits": 100,
        },
        headers=auth_context["headers"],
    )
    simulation_id = create.json()["simulationId"]
    wait_for_simulation(api_client, simulation_id, headers=auth_context["headers"])

    exported = api_client.get(
        f"/simulations/{simulation_id}/export",
        params={"format": "pdf"},
        headers=auth_context["headers"],
    )
    assert exported.status_code == 200
    assert exported.content.startswith(b"%PDF")
    assert exported.headers["content-type"].startswith("application/pdf")


def test_build_simulation_results_pdf_accepts_api_payload() -> None:
    payload = {
        "simulationId": "00000000-0000-0000-0000-000000000001",
        "engineVersion": "runtime-core@1.8.0",
        "gameVersionContentHash": "a" * 64,
        "summary": {
            "rtp": 0.96,
            "uncappedRtp": 0.96,
            "volatility": 3.2,
            "hitFrequency": 0.28,
        },
        "hitFrequency": {"winningSpinCount": 5, "losingSpinCount": 15},
        "rtpValidation": None,
        "rtpDecompositionChart": {
            "BASE": 60,
            "FREE_SPINS": 36,
            "HOLD_AND_WIN": 0,
            "JACKPOT": 0,
            "totalRtp": 96,
        },
        "featureFrequencies": [],
        "exposure": {
            "truncationRate": 0,
            "totalTruncatedMinorUnits": 0,
            "cappedRtp": 0.96,
            "uncappedRtp": 0.96,
            "rtpDifference": 0,
            "exposureCapApplied": False,
        },
        "recommendations": [],
    }
    pdf = build_simulation_results_pdf(payload)
    assert pdf.startswith(b"%PDF")
