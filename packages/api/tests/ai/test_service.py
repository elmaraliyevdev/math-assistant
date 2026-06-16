"""AIService unit tests with mocked dependencies."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest

from app.ai.service import AIService
from app.schemas.mathematics import (
    CalibrateResponse,
    CalibrationResultResponse,
    DiscrepancyAnalysisResponse,
    FeatureProbabilityItem,
    TheoreticalAnalysisResponse,
    TheoreticalRtpResponse,
)
from app.schemas.simulations import (
    ExposureSummary,
    RtpDecompositionChartSummary,
    RtpDecompositionSummary,
    SimulationCompareResponse,
    SimulationComparisonMetrics,
    SimulationCompareEntry,
    SimulationDetailResponse,
    SimulationProgress,
    SimulationResultsResponse,
    SimulationResultsSummary,
    SimulationResultsTotals,
)
from tests.ai.test_engines import _results


def _theoretical() -> TheoreticalAnalysisResponse:
    return TheoreticalAnalysisResponse(
        rtp=TheoreticalRtpResponse(
            totalRtp=0.0512,
            baseRtp=0.0512,
            scatterRtp=0.0,
            lineRtp=0.0512,
            outcomeCount=3125,
            reelSetId="base_game",
        ),
        feature_probabilities=[
            FeatureProbabilityItem(trigger="FREE_SPINS", probability=0.027, one_in_x=37.0),
        ],
        engine_version="runtime-core@1.8.0",
    )


def _detail(sim_id: uuid.UUID, version_id: uuid.UUID) -> SimulationDetailResponse:
    return SimulationDetailResponse(
        id=sim_id,
        game_version_id=version_id,
        status="completed",
        spin_count=100,
        completed_spin_count=100,
        bet_minor_units=100,
        event_log_mode="none",
        created_at="2026-01-01T00:00:00Z",
        started_at="2026-01-01T00:00:01Z",
        completed_at="2026-01-01T00:00:02Z",
        cancel_requested=False,
        worker_id="worker-1",
        error_message=None,
        progress=SimulationProgress(completed_spins=100, percentage=100),
    )


@pytest.mark.asyncio
async def test_ai_service_analyze_and_recommend(valid_canonical_json: dict) -> None:
    sim_id = uuid.uuid4()
    version_id = uuid.uuid4()
    auth = AsyncMock()
    auth.organization_ids = [uuid.uuid4()]

    simulations = AsyncMock()
    simulations.get_simulation.return_value = _detail(sim_id, version_id)
    simulations.get_simulation_results.return_value = _results().model_copy(
        update={"simulation_id": sim_id},
    )

    mathematics = AsyncMock()
    mathematics.theoretical_analysis.return_value = _theoretical()
    mathematics.calibrate.return_value = CalibrateResponse(
        theoreticalRtp=_theoretical().rtp,
        featureProbabilities=[],
        calibration=CalibrationResultResponse(
            targetRtp=96.0,
            theoreticalRtp=5.12,
            simulatedRtp=51.0,
            targetDelta=-90.88,
            theoryVsSimulationDelta=45.88,
            withinTolerance=False,
            tolerance=0.1,
        ),
        discrepancy=DiscrepancyAnalysisResponse(items=[], summary="gap"),
        recommendations=[],
        engineVersion="runtime-core@1.8.0",
    )

    game_versions = AsyncMock()
    game_versions.get_by_id_for_organizations.return_value = AsyncMock(
        canonical_json=valid_canonical_json,
        game_id=uuid.uuid4(),
    )
    games = AsyncMock()
    games.get_by_id_for_organizations.return_value = AsyncMock(
        organization_id=auth.organization_ids[0],
    )

    service = AIService(
        simulations=simulations,
        mathematics=mathematics,
        game_versions=game_versions,
        games=games,
    )

    analysis = await service.analyze_simulation(auth, sim_id)
    assert analysis["simulationId"] == str(sim_id)

    recommendation = await service.recommend_for_simulation(auth, sim_id, target_rtp=96.0)
    assert recommendation["targetRtp"] == 96.0


@pytest.mark.asyncio
async def test_ai_service_compare_and_explain(valid_canonical_json: dict) -> None:
    sim_a = uuid.uuid4()
    sim_b = uuid.uuid4()
    version_id = uuid.uuid4()
    auth = AsyncMock()
    auth.organization_ids = [uuid.uuid4()]

    detail = _detail(sim_a, version_id)
    compare = SimulationCompareResponse(
        simulations=[
            SimulationCompareEntry(
                simulation_id=sim_a,
                detail=detail,
                results=_results(rtp=0.51).model_copy(update={"simulation_id": sim_a}),
                runtime_duration_ms=1000,
            ),
            SimulationCompareEntry(
                simulation_id=sim_b,
                detail=detail.model_copy(update={"id": sim_b}),
                results=_results(rtp=0.62).model_copy(update={"simulation_id": sim_b}),
                runtime_duration_ms=1200,
            ),
        ],
        comparison=SimulationComparisonMetrics(
            rtp=[],
            volatility=[],
            hit_frequency=[],
            confidence_intervals=[],
            feature_frequency=[],
            rtp_decomposition=[],
        ),
    )

    simulations = AsyncMock()
    simulations.compare_simulations.return_value = compare

    mathematics = AsyncMock()
    mathematics.theoretical_analysis.return_value = _theoretical()

    game_versions = AsyncMock()
    game_versions.get_by_id_for_organizations.return_value = AsyncMock(
        canonical_json=valid_canonical_json,
        game_id=uuid.uuid4(),
    )
    games = AsyncMock()
    games.get_by_id_for_organizations.return_value = AsyncMock(
        organization_id=auth.organization_ids[0],
    )

    service = AIService(
        simulations=simulations,
        mathematics=mathematics,
        game_versions=game_versions,
        games=games,
    )

    comparison = await service.compare_simulations(auth, [sim_a, sim_b])
    assert len(comparison["simulationIds"]) == 2

    explain = await service.explain_game_version(auth, version_id)
    assert explain["gameVersionId"] == str(version_id)
