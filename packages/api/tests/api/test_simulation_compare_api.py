"""Simulation comparison API tests."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
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
from tests.api.test_simulations_api import (
    _create_game_version,
    wait_for_simulation,
)


def _sample_report(*, rtp: float = 0.96, spin_count: int = 10) -> MathematicsReport:
    total_bet = spin_count * 100
    total_win = int(total_bet * rtp)
    return MathematicsReport(
        rtp=RTPResult(
            rtp=rtp,
            uncapped_rtp=rtp,
            total_bet_minor_units=total_bet,
            total_win_minor_units=total_win,
            uncapped_win_minor_units=total_win,
        ),
        hit_frequency=HitFrequencyResult(
            hit_frequency=0.25,
            winning_spin_count=3,
            losing_spin_count=spin_count - 3,
        ),
        feature_frequencies=(),
        jackpot_frequencies=(),
        volatility=VolatilityResult(
            mean_win_minor_units=total_win / spin_count,
            variance=10.0,
            standard_deviation=3.0,
            coefficient_of_variation=1.0,
        ),
        exposure=ExposureAnalysisResult(
            truncation_rate=0.0,
            total_truncated_minor_units=0,
            capped_rtp=rtp,
            uncapped_rtp=rtp,
            rtp_difference=0.0,
        ),
        confidence_interval=ConfidenceIntervalResult(
            lower_bound=rtp - 0.05,
            upper_bound=rtp + 0.05,
            confidence_level=0.95,
        ),
        win_distribution=WinDistributionResult(
            total_spins=spin_count,
            bet_minor_units_per_spin=100,
            buckets=(),
        ),
        rtp_decomposition=RtpDecompositionResult(totalRtp=rtp, categories=()),
        spin_count=spin_count,
        engine_version="runtime-core@1.8.0",
    )


def _mock_outcome(*, rtp: float, spin_count: int = 10) -> SimulationExecutionOutcome:
    total_bet = spin_count * 100
    total_win = int(total_bet * rtp)
    return SimulationExecutionOutcome(
        engine_result=EngineSimulationResult(
            spinCount=spin_count,
            shardCount=1,
            elapsedTimeMs=100,
            totalBetMinorUnits=total_bet,
            totalWinMinorUnits=total_win,
            uncappedWinMinorUnits=total_win,
            exposureTruncationCount=0,
            exposureTruncatedMinorUnits=0,
            chainFaultCount=0,
            limitHitCount=0,
            featureTriggerCounts={},
            jackpotCounts={},
            eventSampleCount=0,
            engineVersion="runtime-core@1.8.0",
        ),
        mathematics_report=_sample_report(rtp=rtp, spin_count=spin_count),
    )


def _create_completed_simulation(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
    *,
    rtp: float,
    game_version_id: str | None = None,
) -> str:
    if game_version_id is None:
        game_version_id = _create_game_version(api_client, auth_context, valid_canonical_json)
    with patch(
        "app.jobs.simulation_jobs.execute_simulation_async",
        new_callable=AsyncMock,
        return_value=_mock_outcome(rtp=rtp),
    ):
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
    return created["simulationId"]


def test_compare_simulations_success(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game_version_id = _create_game_version(api_client, auth_context, valid_canonical_json)
    first = _create_completed_simulation(
        api_client,
        auth_context,
        valid_canonical_json,
        rtp=0.51,
        game_version_id=game_version_id,
    )
    second = _create_completed_simulation(
        api_client,
        auth_context,
        valid_canonical_json,
        rtp=0.961,
        game_version_id=game_version_id,
    )
    response = api_client.get(
        f"/simulations/compare?ids={first},{second}",
        headers=auth_context["headers"],
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["simulations"]) == 2
    assert "comparison" in body
    assert len(body["comparison"]["rtp"]) == 2
    assert len(body["comparison"]["rtpDecomposition"]) == 2


def test_compare_simulations_invalid_count(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    only = _create_completed_simulation(api_client, auth_context, valid_canonical_json, rtp=0.96)
    response = api_client.get(
        f"/simulations/compare?ids={only}",
        headers=auth_context["headers"],
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_COMPARISON"


def test_compare_simulations_not_found(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    first = _create_completed_simulation(api_client, auth_context, valid_canonical_json, rtp=0.96)
    missing = uuid.uuid4()
    response = api_client.get(
        f"/simulations/compare?ids={first},{missing}",
        headers=auth_context["headers"],
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "SIMULATION_NOT_FOUND"


def test_compare_simulations_not_completed(
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
        first = api_client.post(
            "/simulations",
            json={"gameVersionId": game_version_id, "spinCount": 10},
            headers=auth_context["headers"],
        ).json()["simulationId"]
        wait_for_simulation(
            api_client,
            first,
            headers=auth_context["headers"],
            expected_status="failed",
        )
    second = _create_completed_simulation(
        api_client,
        auth_context,
        valid_canonical_json,
        rtp=0.96,
        game_version_id=game_version_id,
    )
    response = api_client.get(
        f"/simulations/compare?ids={first},{second}",
        headers=auth_context["headers"],
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_COMPARISON"
