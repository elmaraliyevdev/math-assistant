"""Simulation job infrastructure tests."""

from __future__ import annotations

import asyncio
import time
import uuid
from unittest.mock import AsyncMock, patch

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

from app.adapters.simulation_types import SimulationExecutionOutcome
from app.db.models.simulation import SimulationStatus
from app.db.repositories.simulation_repository import SimulationRepository
from app.config import Settings
from app.jobs.dispatcher import SimulationDispatcher
from app.exceptions.simulation import SimulationJobCancelledError
from app.jobs.models import SimulationJob
from app.jobs.process_pool import SimulationProcessPool
from app.jobs.queue import InMemorySimulationQueue
from app.jobs.worker import SimulationWorker, new_worker_id
from tests.jobs.helpers import run_process_simulation_job


async def _fetch_simulation(
    session_factory,
    simulation_id: uuid.UUID,
):
    async with session_factory() as session:
        return await SimulationRepository(session).get_by_id(simulation_id)


@pytest.fixture
def job_process_pool() -> SimulationProcessPool:
    pool = SimulationProcessPool(max_workers=2)
    pool.start()
    yield pool
    pool.shutdown(wait=True)


@pytest.fixture
def job_settings() -> Settings:
    return Settings(
        simulation_worker_count=2,
        simulation_process_pool_workers=2,
        simulation_spin_wins_detail_limit=10_000,
    )


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


def _engine_result(spin_count: int = 100) -> EngineSimulationResult:
    return EngineSimulationResult(
        spinCount=spin_count,
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
async def test_process_simulation_job_missing_game_version(
    db_session,
    session_factory,
    game_repo,
    game_version_repo,
    simulation_repo,
    sample_game,
    sample_simulation,
    job_process_pool,
    job_settings,
) -> None:
    await game_repo.add(sample_game)
    sample_simulation.status = SimulationStatus.PENDING
    sample_simulation.game_version_id = uuid.uuid4()
    await simulation_repo.add(sample_simulation)
    await db_session.commit()
    simulation_id = sample_simulation.id

    await run_process_simulation_job(
        session_factory,
        simulation_id,
        process_pool=job_process_pool,
        settings=job_settings,
    )

    refreshed = await _fetch_simulation(session_factory, simulation_id)
    assert refreshed is not None
    assert refreshed.status == SimulationStatus.FAILED
    assert refreshed.error_message == "game version not found"


@pytest.mark.asyncio
async def test_poll_cancel_requested_sets_monitor(
    session_factory,
    db_session,
    game_repo,
    game_version_repo,
    simulation_repo,
    sample_game,
    sample_game_version,
    sample_simulation,
) -> None:
    from app.jobs.simulation_jobs import _CancelMonitor, _poll_cancel_requested

    await game_repo.add(sample_game)
    await game_version_repo.add(sample_game_version)
    sample_simulation.status = SimulationStatus.PENDING
    sample_simulation.cancel_requested = True
    await simulation_repo.add(sample_simulation)
    await db_session.commit()

    monitor = _CancelMonitor()
    await _poll_cancel_requested(session_factory, sample_simulation.id, monitor)
    assert monitor.cancelled is True


@pytest.mark.asyncio
async def test_in_memory_queue_enqueue_dequeue() -> None:
    queue = InMemorySimulationQueue()
    job = SimulationJob(simulation_id=uuid.uuid4())
    await queue.enqueue(job)
    assert queue.pending_count == 1
    dequeued = await queue.dequeue()
    assert dequeued == job
    queue.task_done()


@pytest.mark.asyncio
async def test_process_simulation_job_completes(
    db_session,
    session_factory,
    game_repo,
    game_version_repo,
    simulation_repo,
    sample_game,
    sample_game_version,
    sample_simulation,
    valid_canonical_json,
    job_process_pool,
    job_settings,
) -> None:
    await game_repo.add(sample_game)
    sample_game_version.canonical_json = valid_canonical_json
    await game_version_repo.add(sample_game_version)
    sample_simulation.status = SimulationStatus.PENDING
    sample_simulation.spin_count = 10
    await simulation_repo.add(sample_simulation)
    await db_session.commit()
    simulation_id = sample_simulation.id

    outcome = SimulationExecutionOutcome(
        engine_result=_engine_result(spin_count=10),
        mathematics_report=_sample_report(),
    )
    with patch(
        "app.jobs.simulation_jobs.execute_simulation_async",
        new_callable=AsyncMock,
        return_value=outcome,
    ):
        await run_process_simulation_job(
            session_factory,
            simulation_id,
            process_pool=job_process_pool,
            settings=job_settings,
        )

    refreshed = await _fetch_simulation(session_factory, simulation_id)
    assert refreshed is not None
    assert refreshed.status == SimulationStatus.COMPLETED
    assert refreshed.worker_id == "worker-test"
    assert refreshed.started_at is not None


@pytest.mark.asyncio
async def test_process_simulation_job_failure(
    db_session,
    session_factory,
    game_repo,
    game_version_repo,
    simulation_repo,
    sample_game,
    sample_game_version,
    sample_simulation,
    valid_canonical_json,
    job_process_pool,
    job_settings,
) -> None:
    await game_repo.add(sample_game)
    sample_game_version.canonical_json = valid_canonical_json
    await game_version_repo.add(sample_game_version)
    sample_simulation.status = SimulationStatus.PENDING
    await simulation_repo.add(sample_simulation)
    await db_session.commit()
    simulation_id = sample_simulation.id

    with patch(
        "app.jobs.simulation_jobs.execute_simulation_async",
        new_callable=AsyncMock,
        side_effect=RuntimeError("boom"),
    ):
        await run_process_simulation_job(
            session_factory,
            simulation_id,
            process_pool=job_process_pool,
            settings=job_settings,
        )

    refreshed = await _fetch_simulation(session_factory, simulation_id)
    assert refreshed is not None
    assert refreshed.status == SimulationStatus.FAILED
    assert refreshed.error_message == "boom"


@pytest.mark.asyncio
async def test_process_simulation_job_cancel_requested(
    db_session,
    session_factory,
    game_repo,
    game_version_repo,
    simulation_repo,
    sample_game,
    sample_game_version,
    sample_simulation,
    job_process_pool,
    job_settings,
) -> None:
    await game_repo.add(sample_game)
    await game_version_repo.add(sample_game_version)
    sample_simulation.status = SimulationStatus.PENDING
    sample_simulation.cancel_requested = True
    await simulation_repo.add(sample_simulation)
    await db_session.commit()
    simulation_id = sample_simulation.id

    await run_process_simulation_job(
        session_factory,
        simulation_id,
        process_pool=job_process_pool,
        settings=job_settings,
    )

    refreshed = await _fetch_simulation(session_factory, simulation_id)
    assert refreshed is not None
    assert refreshed.status == SimulationStatus.FAILED
    assert refreshed.error_message == "Simulation cancelled"


@pytest.mark.asyncio
async def test_process_simulation_job_invalid_event_log_mode(
    db_session,
    session_factory,
    game_repo,
    game_version_repo,
    simulation_repo,
    sample_game,
    sample_game_version,
    sample_simulation,
    job_process_pool,
    job_settings,
) -> None:
    await game_repo.add(sample_game)
    await game_version_repo.add(sample_game_version)
    sample_simulation.status = SimulationStatus.PENDING
    sample_simulation.event_log_mode = "invalid-mode"
    await simulation_repo.add(sample_simulation)
    await db_session.commit()
    simulation_id = sample_simulation.id

    await run_process_simulation_job(
        session_factory,
        simulation_id,
        process_pool=job_process_pool,
        settings=job_settings,
    )

    refreshed = await _fetch_simulation(session_factory, simulation_id)
    assert refreshed is not None
    assert refreshed.status == SimulationStatus.FAILED
    assert "unsupported eventLogMode" in (refreshed.error_message or "")


@pytest.mark.asyncio
async def test_process_simulation_job_cancelled_during_execution(
    db_session,
    session_factory,
    game_repo,
    game_version_repo,
    simulation_repo,
    sample_game,
    sample_game_version,
    sample_simulation,
    valid_canonical_json,
    job_process_pool,
    job_settings,
) -> None:
    await game_repo.add(sample_game)
    sample_game_version.canonical_json = valid_canonical_json
    await game_version_repo.add(sample_game_version)
    sample_simulation.status = SimulationStatus.PENDING
    await simulation_repo.add(sample_simulation)
    await db_session.commit()
    simulation_id = sample_simulation.id

    def raise_cancelled(*args, **kwargs) -> SimulationExecutionOutcome:
        raise SimulationJobCancelledError

    with patch(
        "app.jobs.simulation_jobs.execute_simulation_async",
        new_callable=AsyncMock,
        side_effect=raise_cancelled,
    ):
        await run_process_simulation_job(
            session_factory,
            simulation_id,
            process_pool=job_process_pool,
            settings=job_settings,
        )

    refreshed = await _fetch_simulation(session_factory, simulation_id)
    assert refreshed is not None
    assert refreshed.status == SimulationStatus.FAILED
    assert refreshed.error_message == "Simulation cancelled"


@pytest.mark.asyncio
async def test_process_simulation_job_missing_simulation(
    session_factory,
    job_process_pool,
    job_settings,
) -> None:
    await run_process_simulation_job(
        session_factory,
        uuid.uuid4(),
        process_pool=job_process_pool,
        settings=job_settings,
    )


@pytest.mark.asyncio
async def test_process_simulation_job_skips_non_pending(
    db_session,
    session_factory,
    game_repo,
    game_version_repo,
    simulation_repo,
    sample_game,
    sample_game_version,
    sample_simulation,
    job_process_pool,
    job_settings,
) -> None:
    await game_repo.add(sample_game)
    await game_version_repo.add(sample_game_version)
    sample_simulation.status = SimulationStatus.COMPLETED
    await simulation_repo.add(sample_simulation)
    await db_session.commit()

    await run_process_simulation_job(
        session_factory,
        sample_simulation.id,
        process_pool=job_process_pool,
        settings=job_settings,
    )


@pytest.mark.asyncio
async def test_progress_callback_persists_updates(
    db_session,
    session_factory,
    game_repo,
    game_version_repo,
    simulation_repo,
    sample_game,
    sample_game_version,
    sample_simulation,
) -> None:
    await game_repo.add(sample_game)
    await game_version_repo.add(sample_game_version)
    sample_simulation.status = SimulationStatus.RUNNING
    sample_simulation.spin_count = 100
    await simulation_repo.add(sample_simulation)
    await db_session.commit()
    simulation_id = sample_simulation.id

    from app.jobs.simulation_jobs import _progress_callback

    callback, progress_tasks = _progress_callback(
        session_factory,
        simulation_id=simulation_id,
    )
    callback(25, 100)
    await asyncio.gather(*progress_tasks)

    refreshed = await _fetch_simulation(session_factory, simulation_id)
    assert refreshed is not None
    assert refreshed.completed_spin_count == 25


@pytest.mark.asyncio
async def test_dispatcher_start_stop(session_factory, job_process_pool, job_settings) -> None:
    dispatcher = SimulationDispatcher(
        session_factory=session_factory,
        process_pool=job_process_pool,
        settings=job_settings,
    )
    await dispatcher.start()
    assert len(dispatcher._workers) == job_settings.simulation_worker_count
    await dispatcher.stop()
    assert dispatcher._workers == []


@pytest.mark.asyncio
async def test_dispatcher_recovers_pending_jobs_on_start(
    db_session,
    session_factory,
    game_repo,
    game_version_repo,
    simulation_repo,
    sample_game,
    sample_game_version,
    sample_simulation,
    valid_canonical_json,
    job_process_pool,
    job_settings,
) -> None:
    await game_repo.add(sample_game)
    sample_game_version.canonical_json = valid_canonical_json
    await game_version_repo.add(sample_game_version)
    sample_simulation.status = SimulationStatus.PENDING
    sample_simulation.spin_count = 5
    await simulation_repo.add(sample_simulation)
    await db_session.commit()
    simulation_id = sample_simulation.id

    outcome = SimulationExecutionOutcome(
        engine_result=_engine_result(spin_count=5),
        mathematics_report=_sample_report(),
    )
    dispatcher = SimulationDispatcher(
        session_factory=session_factory,
        process_pool=job_process_pool,
        settings=job_settings,
    )
    with patch(
        "app.jobs.simulation_jobs.execute_simulation_async",
        new_callable=AsyncMock,
        return_value=outcome,
    ):
        await dispatcher.start()
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            refreshed = await _fetch_simulation(session_factory, simulation_id)
            if refreshed and refreshed.status == SimulationStatus.COMPLETED:
                break
            await asyncio.sleep(0.05)
        await dispatcher.stop()

    refreshed = await _fetch_simulation(session_factory, simulation_id)
    assert refreshed is not None
    assert refreshed.status == SimulationStatus.COMPLETED


@pytest.mark.asyncio
async def test_worker_processes_enqueued_job(
    db_session,
    session_factory,
    game_repo,
    game_version_repo,
    simulation_repo,
    sample_game,
    sample_game_version,
    sample_simulation,
    valid_canonical_json,
    job_process_pool,
    job_settings,
) -> None:
    await game_repo.add(sample_game)
    sample_game_version.canonical_json = valid_canonical_json
    await game_version_repo.add(sample_game_version)
    sample_simulation.status = SimulationStatus.PENDING
    sample_simulation.spin_count = 5
    await simulation_repo.add(sample_simulation)
    await db_session.commit()
    simulation_id = sample_simulation.id

    queue = InMemorySimulationQueue()
    worker = SimulationWorker(
        worker_id=new_worker_id(),
        queue=queue,
        session_factory=session_factory,
        process_pool=job_process_pool,
        settings=job_settings,
    )
    outcome = SimulationExecutionOutcome(
        engine_result=_engine_result(spin_count=5),
        mathematics_report=_sample_report(),
    )
    with patch(
        "app.jobs.simulation_jobs.execute_simulation_async",
        new_callable=AsyncMock,
        return_value=outcome,
    ):
        await worker.start()
        await queue.enqueue(SimulationJob(simulation_id=simulation_id))
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            refreshed = await _fetch_simulation(session_factory, simulation_id)
            if refreshed and refreshed.status == SimulationStatus.COMPLETED:
                break
            await asyncio.sleep(0.05)
        await worker.stop()

    refreshed = await _fetch_simulation(session_factory, simulation_id)
    assert refreshed is not None
    assert refreshed.status == SimulationStatus.COMPLETED


def test_new_worker_id_unique() -> None:
    assert new_worker_id() != new_worker_id()
