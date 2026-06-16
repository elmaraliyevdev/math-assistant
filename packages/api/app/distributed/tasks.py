"""Celery tasks for distributed simulation execution."""

from __future__ import annotations

import asyncio
import threading
import uuid

from app.config import get_settings
from app.db.repositories.game_version_repository import GameVersionRepository
from app.db.repositories.simulation_repository import SimulationRepository
from app.db.session import create_engine, create_session_factory
from app.distributed.aggregation_service import AggregationService
from app.distributed.celery_app import celery_app
from app.distributed.orchestration_service import OrchestrationService
from app.distributed.shard_service import ShardService
from app.distributed.worker_service import execute_simulation_shard
from app.jobs.simulation_logging import log_simulation_event

_test_session_factory = None


def _session_factory():
    if _test_session_factory is not None:
        return _test_session_factory
    settings = get_settings()
    engine = create_engine(settings)
    return create_session_factory(engine)


def _run_async(coro):
    """Run async coroutine from synchronous Celery worker context."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    result: dict[str, object] = {}
    error: dict[str, BaseException] = {}

    def runner() -> None:
        try:
            result["value"] = asyncio.run(coro)
        except BaseException as exc:
            error["exc"] = exc

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    thread.join(timeout=120)
    if error:
        raise error["exc"]
    return result.get("value")


@celery_app.task(name="app.distributed.tasks.orchestrate_simulation", bind=True)
def orchestrate_simulation(self, simulation_id: str) -> int:
    return _run_async(_orchestrate_async(uuid.UUID(simulation_id)))


@celery_app.task(name="app.distributed.tasks.run_simulation_shard", bind=True)
def run_simulation_shard(self, simulation_id: str, shard_index: int) -> str:
    return _run_async(
        _run_shard_async(
            uuid.UUID(simulation_id),
            shard_index,
            worker_id=self.request.hostname or "celery-worker",
            celery_task_id=self.request.id,
        ),
    )


async def _orchestrate_async(simulation_id: uuid.UUID) -> int:
    settings = get_settings()
    factory = _session_factory()
    orchestrator = OrchestrationService(factory, settings)
    shards = await orchestrator.prepare_shards(simulation_id)
    if not shards:
        return 0
    return await orchestrator.dispatch_shards(simulation_id)


async def _run_shard_async(
    simulation_id: uuid.UUID,
    shard_index: int,
    *,
    worker_id: str,
    celery_task_id: str | None,
) -> str:
    settings = get_settings()
    factory = _session_factory()
    shard_service = ShardService(factory)
    aggregation = AggregationService(factory, settings)

    async with factory() as session:
        simulation = await SimulationRepository(session).get_by_id(simulation_id)
        if simulation is None:
            return "missing"
        if simulation.cancel_requested:
            await shard_service.mark_cancelled_shards(simulation_id)
            return "cancelled"

    await shard_service.mark_running(
        simulation_id,
        shard_index,
        worker_id=worker_id,
        celery_task_id=celery_task_id,
    )

    try:
        async with factory() as session:
            simulation = await SimulationRepository(session).get_by_id(simulation_id)
            if simulation is None:
                return "missing"
            if simulation.cancel_requested:
                await shard_service.mark_cancelled_shards(simulation_id)
                return "cancelled"
            game_version = await GameVersionRepository(session).get_by_id(
                simulation.game_version_id,
            )
            if game_version is None:
                await shard_service.mark_failed(
                    simulation_id,
                    shard_index,
                    error_message="game version not found",
                )
                await aggregation.try_finalize(simulation_id)
                return "failed"

        partial = execute_simulation_shard(
            simulation_id=simulation_id,
            game_canonical_json=game_version.canonical_json,
            spin_count=simulation.spin_count,
            bet_minor_units=simulation.bet_minor_units,
            event_log_mode=simulation.event_log_mode,
            master_seed=simulation.master_seed,
            engine_version=game_version.engine_version,
            shard_index=shard_index,
            total_shard_count=simulation.total_shards,
        )
        await shard_service.mark_completed(
            simulation_id,
            shard_index,
            partial=partial,
        )
        log_simulation_event(
            "simulation_shard_completed",
            simulation_id=str(simulation_id),
            shard_index=shard_index,
            distributed=True,
        )
    except Exception as exc:
        await shard_service.mark_failed(
            simulation_id,
            shard_index,
            error_message=str(exc),
        )
        log_simulation_event(
            "simulation_shard_failed",
            simulation_id=str(simulation_id),
            shard_index=shard_index,
            error=str(exc),
        )

    await aggregation.try_finalize(simulation_id)
    return "done"
