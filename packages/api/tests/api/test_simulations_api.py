"""Simulation API integration tests."""

from __future__ import annotations

import asyncio
import threading
import time
import uuid
from unittest.mock import AsyncMock, patch
from uuid import UUID

from fastapi.testclient import TestClient


def wait_for_simulation(
    client: TestClient,
    simulation_id: str | UUID,
    *,
    headers: dict[str, str],
    expected_status: str = "completed",
    timeout_seconds: float = 30.0,
) -> dict:
    deadline = time.monotonic() + timeout_seconds
    last_body: dict | None = None
    while time.monotonic() < deadline:
        response = client.get(
            f"/simulations/{simulation_id}",
            headers=headers,
        )
        assert response.status_code == 200
        last_body = response.json()
        if last_body["status"] == expected_status:
            return last_body
        if last_body["status"] == "failed" and expected_status != "failed":
            msg = f"simulation failed: {last_body.get('errorMessage')}"
            raise AssertionError(msg)
        time.sleep(0.05)
    msg = f"timed out waiting for {expected_status}, last={last_body}"
    raise AssertionError(msg)


def _create_game_version(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> str:
    game = api_client.post(
        "/games",
        json={
            "name": "Simulation Host",
            "description": "Sim tests",
            "organizationId": auth_context["organization_id"],
        },
        headers=auth_context["headers"],
    )
    assert game.status_code == 201
    game_id = game.json()["id"]
    version = api_client.post(
        f"/games/{game_id}/versions",
        json={
            "canonicalJson": valid_canonical_json,
            "engineVersion": "runtime-core@1.8.0",
        },
        headers=auth_context["headers"],
    )
    assert version.status_code == 201
    return version.json()["id"]


def test_create_simulation_success(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game_version_id = _create_game_version(api_client, auth_context, valid_canonical_json)
    response = api_client.post(
        "/simulations",
        json={
            "gameVersionId": game_version_id,
            "spinCount": 50,
            "betMinorUnits": 100,
            "eventLogMode": "none",
            "masterSeed": "test-seed",
        },
        headers=auth_context["headers"],
    )
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "pending"
    assert "simulationId" in body

    detail = wait_for_simulation(
        api_client,
        body["simulationId"],
        headers=auth_context["headers"],
    )
    assert detail["status"] == "completed"
    assert detail["completedSpinCount"] == 50
    assert detail["spinCount"] == 50
    assert detail["progress"]["completedSpins"] == 50
    assert detail["progress"]["percentage"] == 100.0


def test_create_simulation_persists_results(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game_version_id = _create_game_version(api_client, auth_context, valid_canonical_json)
    created = api_client.post(
        "/simulations",
        json={
            "gameVersionId": game_version_id,
            "spinCount": 20,
            "betMinorUnits": 100,
        },
        headers=auth_context["headers"],
    ).json()
    wait_for_simulation(
        api_client,
        created["simulationId"],
        headers=auth_context["headers"],
    )
    results = api_client.get(
        f"/simulations/{created['simulationId']}/results",
        headers=auth_context["headers"],
    )
    assert results.status_code == 200
    body = results.json()
    assert body["simulationId"] == created["simulationId"]
    assert "rtp" in body["summary"]
    assert body["totals"]["totalBetMinorUnits"] >= 0
    assert "rtpValidation" in body
    assert body["rtpValidation"] is not None
    assert "targetRtp" in body["rtpValidation"]
    assert "withinTolerance" in body["rtpValidation"]
    assert "rtpDecompositionChart" in body
    chart = body["rtpDecompositionChart"]
    assert "BASE" in chart
    assert "FREE_SPINS" in chart
    assert "HOLD_AND_WIN" in chart
    assert "JACKPOT" in chart
    assert "featureValidation" in body
    assert isinstance(body["featureValidation"], list)
    assert "recommendations" in body
    assert isinstance(body["recommendations"], list)


def test_create_simulation_game_version_not_found(
    api_client: TestClient,
    auth_context: dict,
) -> None:
    response = api_client.post(
        "/simulations",
        json={
            "gameVersionId": str(uuid.uuid4()),
            "spinCount": 10,
        },
        headers=auth_context["headers"],
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "GAME_VERSION_NOT_FOUND"


def test_create_simulation_failure_sets_failed_status(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game_version_id = _create_game_version(api_client, auth_context, valid_canonical_json)
    with patch(
        "app.jobs.simulation_jobs.execute_simulation_async",
        new_callable=AsyncMock,
        side_effect=RuntimeError("simulation exploded"),
    ):
        response = api_client.post(
            "/simulations",
            json={
                "gameVersionId": game_version_id,
                "spinCount": 10,
            },
            headers=auth_context["headers"],
        )
        assert response.status_code == 202
        body = response.json()
        assert body["status"] == "pending"

        detail = wait_for_simulation(
            api_client,
            body["simulationId"],
            headers=auth_context["headers"],
            expected_status="failed",
        )
    assert detail["status"] == "failed"
    assert detail["errorMessage"] == "simulation exploded"


def test_get_simulation_results_not_ready(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game_version_id = _create_game_version(api_client, auth_context, valid_canonical_json)
    created = api_client.post(
        "/simulations",
        json={"gameVersionId": game_version_id, "spinCount": 5},
        headers=auth_context["headers"],
    ).json()
    results = api_client.get(
        f"/simulations/{created['simulationId']}/results",
        headers=auth_context["headers"],
    )
    assert results.status_code == 409
    assert results.json()["error"]["code"] == "SIMULATION_RESULTS_NOT_READY"


def test_list_simulations_with_filters(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game_version_id = _create_game_version(api_client, auth_context, valid_canonical_json)
    created = api_client.post(
        "/simulations",
        json={"gameVersionId": game_version_id, "spinCount": 10, "betMinorUnits": 100},
        headers=auth_context["headers"],
    ).json()
    wait_for_simulation(
        api_client,
        created["simulationId"],
        headers=auth_context["headers"],
    )
    listed = api_client.get(
        "/simulations",
        params={
            "status": "completed",
            "gameVersionId": game_version_id,
            "page": 1,
            "pageSize": 10,
        },
        headers=auth_context["headers"],
    )
    assert listed.status_code == 200
    body = listed.json()
    assert body["total"] >= 1
    assert body["items"][0]["gameVersionId"] == game_version_id


def test_get_simulation_not_found(
    api_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = api_client.get(
        f"/simulations/{uuid.uuid4()}",
        headers=auth_headers,
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "SIMULATION_NOT_FOUND"


def test_simulation_propagates_request_id(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game_version_id = _create_game_version(api_client, auth_context, valid_canonical_json)
    response = api_client.post(
        "/simulations",
        json={"gameVersionId": game_version_id, "spinCount": 5},
        headers={
            **auth_context["headers"],
            "X-Request-Id": "sim-create-req-1",
        },
    )
    assert response.status_code == 202
    assert response.headers["X-Request-Id"] == "sim-create-req-1"


def test_cancel_pending_simulation(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game_version_id = _create_game_version(api_client, auth_context, valid_canonical_json)
    started = threading.Event()

    async def blocked_execute(*args, **kwargs) -> None:
        started.set()
        while not (kwargs.get("should_cancel") and kwargs["should_cancel"]()):
            await asyncio.sleep(0.01)
        from app.exceptions.simulation import SimulationJobCancelledError

        raise SimulationJobCancelledError

    with patch(
        "app.jobs.simulation_jobs.execute_simulation_async",
        new_callable=AsyncMock,
        side_effect=blocked_execute,
    ):
        created = api_client.post(
            "/simulations",
            json={"gameVersionId": game_version_id, "spinCount": 100},
            headers=auth_context["headers"],
        ).json()
        assert started.wait(timeout=5)
        cancel = api_client.post(
            f"/simulations/{created['simulationId']}/cancel",
            headers=auth_context["headers"],
        )
        assert cancel.status_code == 202
        assert cancel.json()["cancelRequested"] is True

        final = wait_for_simulation(
            api_client,
            created["simulationId"],
            headers=auth_context["headers"],
            expected_status="failed",
            timeout_seconds=30.0,
        )
    assert final["errorMessage"] == "Simulation cancelled"


def test_cancel_completed_simulation_not_allowed(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
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
    cancel = api_client.post(
        f"/simulations/{created['simulationId']}/cancel",
        headers=auth_context["headers"],
    )
    assert cancel.status_code == 409
    assert cancel.json()["error"]["code"] == "SIMULATION_CANCEL_NOT_ALLOWED"


def test_multiple_concurrent_simulations(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    from runtime_core.mathematical.models import (
        ConfidenceIntervalResult,
        ExposureAnalysisResult,
        HitFrequencyResult,
        MathematicsReport,
        RTPResult,
        RtpDecompositionResult,
        VolatilityResult,
        WinDistributionResult,
    )
    from runtime_core.simulation.models import SimulationResult as EngineSimulationResult

    from app.adapters.simulation import SimulationExecutionOutcome

    game_version_id = _create_game_version(api_client, auth_context, valid_canonical_json)
    outcome = SimulationExecutionOutcome(
        engine_result=EngineSimulationResult(
            spinCount=15,
            shardCount=1,
            elapsedTimeMs=1,
            totalBetMinorUnits=1500,
            totalWinMinorUnits=1440,
            uncappedWinMinorUnits=1440,
            exposureTruncationCount=0,
            exposureTruncatedMinorUnits=0,
            chainFaultCount=0,
            limitHitCount=0,
            featureTriggerCounts={},
            jackpotCounts={},
            eventSampleCount=0,
            engineVersion="runtime-core@1.8.0",
        ),
        mathematics_report=MathematicsReport(
            rtp=RTPResult(
                rtp=0.96,
                uncapped_rtp=0.96,
                total_bet_minor_units=1500,
                total_win_minor_units=1440,
                uncapped_win_minor_units=1440,
            ),
            hit_frequency=HitFrequencyResult(
                hit_frequency=0.25,
                winning_spin_count=4,
                losing_spin_count=11,
            ),
            feature_frequencies=(),
            jackpot_frequencies=(),
            volatility=VolatilityResult(
                mean_win_minor_units=96.0,
                variance=100.0,
                standard_deviation=10.0,
                coefficient_of_variation=1.0,
            ),
            exposure=ExposureAnalysisResult(
                truncation_rate=0.0,
                total_truncated_minor_units=0,
                capped_rtp=0.96,
                uncapped_rtp=0.96,
                rtp_difference=0.0,
            ),
            confidence_interval=ConfidenceIntervalResult(
                lower_bound=0.9,
                upper_bound=1.0,
                confidence_level=0.95,
            ),
            win_distribution=WinDistributionResult(
                total_spins=15,
                bet_minor_units_per_spin=100,
                buckets=(),
            ),
            rtp_decomposition=RtpDecompositionResult(totalRtp=0.96, categories=()),
            spin_count=15,
            engine_version="runtime-core@1.8.0",
        ),
    )
    ids = []
    with patch(
        "app.jobs.simulation_jobs.execute_simulation_async",
        new_callable=AsyncMock,
        return_value=outcome,
    ):
        for _ in range(3):
            response = api_client.post(
                "/simulations",
                json={"gameVersionId": game_version_id, "spinCount": 15},
                headers=auth_context["headers"],
            )
            assert response.status_code == 202
            simulation_id = response.json()["simulationId"]
            ids.append(simulation_id)
            wait_for_simulation(
                api_client,
                simulation_id,
                headers=auth_context["headers"],
            )

    assert len(ids) == 3
