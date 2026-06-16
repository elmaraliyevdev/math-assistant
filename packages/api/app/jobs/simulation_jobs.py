"""Simulation job definitions and execution."""

from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from runtime_core.domain.game_version import GameVersion
from runtime_core.runtime.events import EventLogMode
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.adapters.simulation import build_simulation_profile
from app.adapters.simulation_runner import execute_simulation_async
from app.config import Settings
from app.db.models.simulation import Simulation, SimulationStatus
from app.db.models.simulation_result import SimulationResult
from app.db.repositories.game_version_repository import GameVersionRepository
from app.db.repositories.simulation_repository import SimulationRepository
from app.db.repositories.simulation_result_repository import SimulationResultRepository
from app.exceptions.simulation import SimulationJobCancelledError
from app.jobs.process_pool import SimulationProcessPool
from app.jobs.simulation_logging import log_simulation_event
from app.observability.metrics import SIMULATION_DURATION_SECONDS, MetricsTimer
from app.services.platform_events import notify_simulation_finished_by_id

if TYPE_CHECKING:
    from collections.abc import Callable


class _CancelMonitor:
    def __init__(self) -> None:
        self.cancelled = False


async def process_simulation_job(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    simulation_id: uuid.UUID,
    worker_id: str,
    process_pool: SimulationProcessPool,
    settings: Settings,
) -> None:
    """Execute one simulation job and persist lifecycle updates."""
    log_simulation_event(
        "simulation_worker_picked_job",
        simulation_id=str(simulation_id),
        worker_id=worker_id,
    )
    with MetricsTimer(SIMULATION_DURATION_SECONDS):
        await _run_simulation_job(
            session_factory,
            simulation_id=simulation_id,
            worker_id=worker_id,
            process_pool=process_pool,
            settings=settings,
        )


async def _wait_for_simulation_row(
    simulations: SimulationRepository,
    simulation_id: uuid.UUID,
    *,
    attempts: int = 10,
    delay_seconds: float = 0.05,
) -> Simulation | None:
    simulation: Simulation | None = None
    for _ in range(attempts):
        simulation = await simulations.get_by_id(simulation_id)
        if simulation is not None:
            return simulation
        await asyncio.sleep(delay_seconds)
    return simulation


async def _run_simulation_job(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    simulation_id: uuid.UUID,
    worker_id: str,
    process_pool: SimulationProcessPool,
    settings: Settings,
) -> None:
    async with session_factory() as session:
        simulations = SimulationRepository(session)
        simulation = await _wait_for_simulation_row(simulations, simulation_id)
        if simulation is None:
            log_simulation_event(
                "simulation_job_missing_row",
                simulation_id=str(simulation_id),
                worker_id=worker_id,
            )
            return

        if simulation.cancel_requested:
            await _mark_cancelled(simulations, simulation)
            await session.commit()
            return

        if simulation.status != SimulationStatus.PENDING:
            return

        spin_count = simulation.spin_count
        simulation.status = SimulationStatus.RUNNING
        simulation.started_at = datetime.now(tz=UTC)
        simulation.worker_id = worker_id
        simulation.completed_spin_count = 0
        await simulations.save(simulation)
        await session.commit()

    log_simulation_event(
        "simulation_started",
        simulation_id=str(simulation_id),
        worker_id=worker_id,
        spin_count=spin_count,
    )

    monitor = _CancelMonitor()
    poll_task = asyncio.create_task(
        _poll_cancel_requested(session_factory, simulation_id, monitor),
    )
    progress_tasks: list[asyncio.Task[None]] = []
    try:
        async with session_factory() as session:
            simulations = SimulationRepository(session)
            game_versions = GameVersionRepository(session)
            results = SimulationResultRepository(session)

            simulation = await simulations.get_by_id(simulation_id)
            if simulation is None:
                return

            if simulation.cancel_requested or monitor.cancelled:
                await _mark_cancelled(simulations, simulation)
                await session.commit()
                return

            game_version = await game_versions.get_by_id(simulation.game_version_id)
            if game_version is None:
                await _mark_failed(
                    simulations,
                    simulation,
                    error_message="game version not found",
                )
                await session.commit()
                return

            try:
                event_log_mode = _parse_event_log_mode(simulation.event_log_mode)
            except ValueError as exc:
                await _mark_failed(simulations, simulation, error_message=str(exc))
                await session.commit()
                return

            profile = build_simulation_profile(
                simulation_id=simulation.id,
                spin_count=simulation.spin_count,
                bet_minor_units=simulation.bet_minor_units,
                event_log_mode=event_log_mode,
                master_seed=simulation.master_seed,
                engine_version=game_version.engine_version,
                shard_count=None,
            )
            game = GameVersion.model_validate(game_version.canonical_json)

            def should_cancel() -> bool:
                return monitor.cancelled

            on_progress, progress_tasks = _progress_callback(
                session_factory,
                simulation_id=simulation_id,
            )

            outcome = await execute_simulation_async(
                game,
                profile,
                simulation_id=simulation.id,
                process_pool=process_pool.executor(),
                on_progress=on_progress,
                should_cancel=should_cancel,
                spin_wins_detail_limit=settings.simulation_spin_wins_detail_limit,
            )

            if monitor.cancelled:
                session.expire_all()
                simulation = await simulations.get_by_id(simulation_id)
                if simulation is not None:
                    await _mark_cancelled(simulations, simulation)
                    await session.commit()
                return

            session.expire_all()
            simulation = await simulations.get_by_id(simulation_id)
            if simulation is None:
                return

            if simulation.cancel_requested or monitor.cancelled:
                await _mark_cancelled(simulations, simulation)
                await session.commit()
                return

            report = outcome.mathematics_report
            engine_result = outcome.engine_result
            await results.add(
                SimulationResult(
                    simulation_id=simulation.id,
                    total_bet_minor_units=engine_result.total_bet_minor_units,
                    total_win_minor_units=engine_result.total_win_minor_units,
                    uncapped_win_minor_units=engine_result.uncapped_win_minor_units,
                    rtp=report.rtp.rtp,
                    volatility=report.volatility.standard_deviation,
                    hit_frequency=report.hit_frequency.hit_frequency,
                    mathematics_report=report.model_dump(mode="json", by_alias=True),
                ),
            )

            simulation.status = SimulationStatus.COMPLETED
            simulation.completed_spin_count = simulation.spin_count
            simulation.completed_at = datetime.now(tz=UTC)
            simulation.error_message = None
            await simulations.save(simulation)
            await session.commit()
            log_simulation_event(
                "simulation_completed",
                simulation_id=str(simulation_id),
                worker_id=worker_id,
                spin_count=simulation.spin_count,
            )
            # Notifications are best-effort. If a notification side-effect fails
            # (e.g., due to SQLAlchemy async context issues in test/in-memory
            # setups), we still want the simulation result to be marked completed.
            try:
                await notify_simulation_finished_by_id(session_factory, simulation_id)
            except Exception as exc:
                log_simulation_event(
                    "simulation_notification_failed",
                    simulation_id=str(simulation_id),
                    worker_id=worker_id,
                    error=str(exc),
                )
    except SimulationJobCancelledError:
        async with session_factory() as session:
            simulations = SimulationRepository(session)
            simulation = await simulations.get_by_id(simulation_id)
            if simulation is not None:
                await _mark_cancelled(simulations, simulation)
                await session.commit()
        log_simulation_event(
            "simulation_cancelled",
            simulation_id=str(simulation_id),
            worker_id=worker_id,
        )
    except Exception as exc:
        async with session_factory() as session:
            simulations = SimulationRepository(session)
            simulation = await simulations.get_by_id(simulation_id)
            if simulation is not None:
                await _mark_failed(simulations, simulation, error_message=str(exc))
                await session.commit()
                try:
                    await notify_simulation_finished_by_id(session_factory, simulation_id)
                except Exception as notify_exc:
                    log_simulation_event(
                        "simulation_notification_failed",
                        simulation_id=str(simulation_id),
                        worker_id=worker_id,
                        error=str(notify_exc),
                    )
        log_simulation_event(
            "simulation_failed",
            simulation_id=str(simulation_id),
            worker_id=worker_id,
            error=str(exc),
        )
    finally:
        poll_task.cancel()
        try:
            await poll_task
        except asyncio.CancelledError:
            pass
        if progress_tasks:
            await asyncio.gather(*progress_tasks, return_exceptions=True)


def _progress_callback(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    simulation_id: uuid.UUID,
) -> tuple[Callable[[int, int], None], list[asyncio.Task[None]]]:
    pending_tasks: list[asyncio.Task[None]] = []

    async def persist_progress(completed: int, total: int) -> None:
        async with session_factory() as progress_session:
            await progress_session.execute(
                update(Simulation)
                .where(
                    Simulation.id == simulation_id,
                    Simulation.status == SimulationStatus.RUNNING,
                )
                .values(completed_spin_count=completed),
            )
            await progress_session.commit()
            percentage = round((completed / total) * 100, 2) if total else 100.0
            log_simulation_event(
                "simulation_progress_updated",
                simulation_id=str(simulation_id),
                completed_spins=completed,
                total_spins=total,
                percentage=percentage,
            )

    def callback(completed: int, total: int) -> None:
        pending_tasks.append(asyncio.create_task(persist_progress(completed, total)))

    return callback, pending_tasks


async def _poll_cancel_requested(
    session_factory: async_sessionmaker[AsyncSession],
    simulation_id: uuid.UUID,
    monitor: _CancelMonitor,
) -> None:
    while not monitor.cancelled:
        async with session_factory() as session:
            simulation = await SimulationRepository(session).get_by_id(simulation_id)
            if simulation is not None and simulation.cancel_requested:
                monitor.cancelled = True
                return
        await asyncio.sleep(0.05)


async def _mark_cancelled(
    simulations: SimulationRepository,
    simulation: Simulation,
) -> None:
    simulation.status = SimulationStatus.FAILED
    simulation.error_message = "Simulation cancelled"
    simulation.completed_at = datetime.now(tz=UTC)
    await simulations.save(simulation)


async def _mark_failed(
    simulations: SimulationRepository,
    simulation: Simulation,
    *,
    error_message: str,
) -> None:
    simulation.status = SimulationStatus.FAILED
    simulation.error_message = error_message
    simulation.completed_at = datetime.now(tz=UTC)
    await simulations.save(simulation)


def _parse_event_log_mode(value: str) -> EventLogMode:
    try:
        return EventLogMode(value)
    except ValueError as exc:
        msg = f"unsupported eventLogMode {value!r}"
        raise ValueError(msg) from exc
