"""Simulation service unit tests."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest
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

from app.auth.context import AuthContext
from app.db.models.simulation import SimulationStatus
from app.exceptions.domain import (
    GameVersionReferenceNotFoundError,
    SimulationCancelNotAllowedError,
    SimulationNotFoundError,
    SimulationResultsNotReadyError,
)
from app.jobs.models import SimulationJob
from app.schemas.simulations import CreateSimulationRequest
from app.services.simulation_service import SimulationService, _parse_status_filter


def _sample_report() -> MathematicsReport:
    return MathematicsReport(
        rtp=RTPResult(
            rtp=0.96,
            uncapped_rtp=0.96,
            total_bet_minor_units=1000,
            total_win_minor_units=960,
            uncapped_win_minor_units=960,
        ),
        hit_frequency=HitFrequencyResult(
            hit_frequency=0.25,
            winning_spin_count=25,
            losing_spin_count=75,
        ),
        feature_frequencies=(),
        jackpot_frequencies=(),
        volatility=VolatilityResult(
            mean_win_minor_units=9.6,
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
            total_spins=100,
            bet_minor_units_per_spin=10,
            buckets=(),
        ),
        rtp_decomposition=RtpDecompositionResult(totalRtp=0.96, categories=()),
        spin_count=100,
        engine_version="runtime-core@1.8.0",
    )


def _engine_result() -> EngineSimulationResult:
    return EngineSimulationResult(
        spinCount=100,
        shardCount=1,
        elapsedTimeMs=5,
        totalBetMinorUnits=1000,
        totalWinMinorUnits=960,
        uncappedWinMinorUnits=960,
        exposureTruncationCount=0,
        exposureTruncatedMinorUnits=0,
        chainFaultCount=0,
        limitHitCount=0,
        featureTriggerCounts={},
        jackpotCounts={},
        eventSampleCount=0,
        engineVersion="runtime-core@1.8.0",
    )


@pytest.mark.asyncio
async def test_create_simulation_enqueues_pending(
    db_session,
    game_repo,
    game_version_repo,
    sample_game,
    sample_game_version,
    valid_canonical_json,
    auth_context: AuthContext,
) -> None:
    await game_repo.add(sample_game)
    sample_game_version.canonical_json = valid_canonical_json
    await game_version_repo.add(sample_game_version)

    queue = AsyncMock()
    commit_calls = 0
    original_commit = db_session.commit

    async def counting_commit() -> None:
        nonlocal commit_calls
        commit_calls += 1
        await original_commit()

    db_session.commit = counting_commit  # type: ignore[method-assign]

    service = SimulationService.from_session(db_session, queue=queue)
    response = await service.create_simulation(
        auth_context,
        CreateSimulationRequest(
            gameVersionId=sample_game_version.id,
            spinCount=100,
            betMinorUnits=10,
        ),
    )
    assert response.status == SimulationStatus.PENDING.value
    assert commit_calls == 1
    queue.enqueue.assert_awaited_once()
    job = queue.enqueue.await_args.args[0]
    assert isinstance(job, SimulationJob)


@pytest.mark.asyncio
async def test_create_simulation_game_version_missing(
    db_session,
    auth_context: AuthContext,
) -> None:
    service = SimulationService.from_session(db_session)
    with pytest.raises(GameVersionReferenceNotFoundError):
        await service.create_simulation(
            auth_context,
            CreateSimulationRequest(
                gameVersionId=uuid.uuid4(),
                spinCount=10,
            ),
        )


@pytest.mark.asyncio
async def test_cancel_simulation_pending(
    db_session,
    game_repo,
    game_version_repo,
    simulation_repo,
    sample_game,
    sample_game_version,
    sample_simulation,
    auth_context: AuthContext,
) -> None:
    await game_repo.add(sample_game)
    await game_version_repo.add(sample_game_version)
    sample_simulation.status = SimulationStatus.PENDING
    await simulation_repo.add(sample_simulation)

    service = SimulationService.from_session(db_session)
    response = await service.cancel_simulation(auth_context, sample_simulation.id)
    assert response.cancel_requested is True
    assert response.status == SimulationStatus.PENDING.value


@pytest.mark.asyncio
async def test_cancel_simulation_not_allowed(
    db_session,
    game_repo,
    game_version_repo,
    simulation_repo,
    sample_game,
    sample_game_version,
    sample_simulation,
    auth_context: AuthContext,
) -> None:
    await game_repo.add(sample_game)
    await game_version_repo.add(sample_game_version)
    sample_simulation.status = SimulationStatus.COMPLETED
    await simulation_repo.add(sample_simulation)

    service = SimulationService.from_session(db_session)
    with pytest.raises(SimulationCancelNotAllowedError):
        await service.cancel_simulation(auth_context, sample_simulation.id)


@pytest.mark.asyncio
async def test_list_get_and_results(
    db_session,
    game_repo,
    game_version_repo,
    simulation_repo,
    simulation_result_repo,
    sample_game,
    sample_game_version,
    sample_simulation,
    sample_simulation_result,
    auth_context: AuthContext,
) -> None:
    await game_repo.add(sample_game)
    await game_version_repo.add(sample_game_version)
    sample_simulation.status = SimulationStatus.COMPLETED
    sample_simulation.completed_spin_count = 1000
    await simulation_repo.add(sample_simulation)
    await simulation_result_repo.add(sample_simulation_result)

    service = SimulationService.from_session(db_session)
    listed = await service.list_simulations(
        auth_context,
        page=1,
        page_size=10,
        status="completed",
        game_version_id=sample_game_version.id,
    )
    assert listed.total == 1

    detail = await service.get_simulation(auth_context, sample_simulation.id)
    assert detail.status == "completed"
    assert detail.progress.percentage == 100.0

    results = await service.get_simulation_results(auth_context, sample_simulation.id)
    assert results.summary.rtp == 0.96


@pytest.mark.asyncio
async def test_get_simulation_not_found(
    db_session,
    auth_context: AuthContext,
) -> None:
    service = SimulationService.from_session(db_session)
    with pytest.raises(SimulationNotFoundError):
        await service.get_simulation(auth_context, uuid.uuid4())


@pytest.mark.asyncio
async def test_get_results_not_ready(
    db_session,
    game_repo,
    game_version_repo,
    simulation_repo,
    sample_game,
    sample_game_version,
    sample_simulation,
    auth_context: AuthContext,
) -> None:
    await game_repo.add(sample_game)
    await game_version_repo.add(sample_game_version)
    sample_simulation.status = SimulationStatus.FAILED
    await simulation_repo.add(sample_simulation)
    service = SimulationService.from_session(db_session)
    with pytest.raises(SimulationResultsNotReadyError):
        await service.get_simulation_results(auth_context, sample_simulation.id)


@pytest.mark.asyncio
async def test_get_results_missing_result_row(
    db_session,
    game_repo,
    game_version_repo,
    simulation_repo,
    sample_game,
    sample_game_version,
    sample_simulation,
    auth_context: AuthContext,
) -> None:
    await game_repo.add(sample_game)
    await game_version_repo.add(sample_game_version)
    sample_simulation.status = SimulationStatus.COMPLETED
    await simulation_repo.add(sample_simulation)
    service = SimulationService.from_session(db_session)
    with pytest.raises(SimulationResultsNotReadyError):
        await service.get_simulation_results(auth_context, sample_simulation.id)


def test_parse_status_filter_valid() -> None:
    assert _parse_status_filter("completed") == SimulationStatus.COMPLETED


def test_parse_status_filter_none() -> None:
    assert _parse_status_filter(None) is None


def test_parse_status_filter_invalid() -> None:
    with pytest.raises(ValueError, match="unsupported status"):
        _parse_status_filter("not-a-status")
