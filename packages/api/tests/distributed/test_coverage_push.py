"""Targeted tests to reach >=90% coverage on app.distributed."""

from __future__ import annotations

import importlib
import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.config import Settings
from app.db.models.simulation import Simulation, SimulationStatus
from app.db.models.simulation_shard import SimulationShard, SimulationShardStatus
from app.distributed.aggregation_service import AggregationService
from app.distributed.monitoring_service import MonitoringService
from app.distributed.orchestration_service import OrchestrationService
from app.distributed.shard_service import ShardService
from app.distributed.tasks import _run_async, _run_shard_async, _session_factory
from runtime_core.simulation import PartialAccumulator


@pytest.mark.asyncio
async def test_run_async_from_running_loop() -> None:
    async def sample() -> str:
        return "ok"

    assert _run_async(sample()) == "ok"


@pytest.mark.asyncio
async def test_run_async_propagates_exception() -> None:
    async def fail() -> None:
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        _run_async(fail())


def test_session_factory_uses_engine_when_no_test_hook() -> None:
    import app.distributed.tasks as tasks

    original = tasks._test_session_factory
    tasks._test_session_factory = None
    try:
        with patch("app.distributed.tasks.create_engine") as engine, patch(
            "app.distributed.tasks.create_session_factory",
            return_value="factory",
        ) as factory_fn:
            assert _session_factory() == "factory"
            engine.assert_called_once()
            factory_fn.assert_called_once()
    finally:
        tasks._test_session_factory = original


def test_celery_eager_config_on_reload(monkeypatch: pytest.MonkeyPatch) -> None:
    eager = Settings(celery_task_always_eager=True)
    monkeypatch.setattr("app.config.get_settings", lambda: eager)
    celery_module = importlib.import_module("app.distributed.celery_app")
    importlib.reload(celery_module)
    assert celery_module.celery_app.conf.task_always_eager is True
    assert celery_module.celery_app.conf.task_eager_propagates is True


@pytest.mark.asyncio
async def test_aggregation_no_shards_returns_false() -> None:
    simulation_id = uuid.uuid4()
    simulation = Simulation(
        id=simulation_id,
        game_version_id=uuid.uuid4(),
        spin_count=10,
        completed_spin_count=0,
        bet_minor_units=100,
        status=SimulationStatus.RUNNING,
    )
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    factory = MagicMock(return_value=session)

    with patch(
        "app.distributed.aggregation_service.SimulationRepository",
    ) as sim_repo_cls, patch(
        "app.distributed.aggregation_service.SimulationShardRepository",
    ) as shard_repo_cls:
        sim_repo_cls.return_value.get_by_id = AsyncMock(return_value=simulation)
        shard_repo_cls.return_value.list_by_simulation_id = AsyncMock(return_value=[])

        service = AggregationService(factory, Settings())
        assert await service.try_finalize(simulation_id) is False


@pytest.mark.asyncio
async def test_aggregation_no_partials_returns_false() -> None:
    simulation_id = uuid.uuid4()
    simulation = Simulation(
        id=simulation_id,
        game_version_id=uuid.uuid4(),
        spin_count=10,
        completed_spin_count=0,
        bet_minor_units=100,
        status=SimulationStatus.RUNNING,
    )
    shard = MagicMock()
    shard.status = SimulationShardStatus.CANCELLED

    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    factory = MagicMock(return_value=session)

    with patch(
        "app.distributed.aggregation_service.SimulationRepository",
    ) as sim_repo_cls, patch(
        "app.distributed.aggregation_service.SimulationShardRepository",
    ) as shard_repo_cls:
        sim_repo_cls.return_value.get_by_id = AsyncMock(return_value=simulation)
        shard_repo_cls.return_value.list_by_simulation_id = AsyncMock(return_value=[shard])

        service = AggregationService(factory, Settings())
        assert await service.try_finalize(simulation_id) is False


@pytest.mark.asyncio
async def test_queue_summary_average_duration() -> None:
    started = datetime.now(tz=UTC) - timedelta(minutes=5)
    completed = datetime.now(tz=UTC)
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.scalar = AsyncMock(side_effect=[0, 0, 1, 0])
    session.execute = AsyncMock(
        return_value=MagicMock(all=MagicMock(return_value=[(started, completed)])),
    )
    monitoring = MonitoringService(MagicMock(return_value=session))

    with patch("app.distributed.celery_app.celery_app") as celery:
        celery.control.inspect.return_value.reserved.return_value = {"w": ["t"]}
        summary = await monitoring.queue_summary()
        assert summary.average_simulation_duration_seconds is not None
        assert summary.pending_tasks == 1


@pytest.mark.asyncio
async def test_orchestrate_method() -> None:
    simulation_id = uuid.uuid4()
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    factory = MagicMock(return_value=session)

    service = OrchestrationService(factory, Settings())
    with patch.object(
        OrchestrationService,
        "prepare_shards",
        AsyncMock(return_value=[MagicMock()]),
    ), patch.object(
        OrchestrationService,
        "dispatch_shards",
        AsyncMock(return_value=1),
    ) as dispatch:
        await service.orchestrate(simulation_id)
        dispatch.assert_awaited_once_with(simulation_id)


@pytest.mark.asyncio
async def test_dispatch_skips_non_pending_shards() -> None:
    simulation_id = uuid.uuid4()
    pending = MagicMock(shard_index=0, status=SimulationShardStatus.PENDING)
    completed = MagicMock(shard_index=1, status=SimulationShardStatus.COMPLETED)

    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    factory = MagicMock(return_value=session)

    with patch(
        "app.distributed.orchestration_service.SimulationShardRepository",
    ) as repo_cls, patch("app.distributed.tasks.run_simulation_shard") as task:
        repo = AsyncMock()
        repo.list_by_simulation_id.return_value = [pending, completed]
        repo.get_by_simulation_and_index.return_value = pending
        repo_cls.return_value = repo
        task.delay.return_value = MagicMock(id="task-1")

        service = OrchestrationService(factory, Settings())
        assert await service.dispatch_shards(simulation_id) == 1


@pytest.mark.asyncio
async def test_prepare_shards_skips_zero_spin_assignments(
    valid_canonical_json: dict,
) -> None:
    simulation_id = uuid.uuid4()
    simulation = Simulation(
        id=simulation_id,
        game_version_id=uuid.uuid4(),
        spin_count=3,
        completed_spin_count=0,
        bet_minor_units=100,
        status=SimulationStatus.PENDING,
        event_log_mode="none",
        master_seed="seed",
    )
    game_version = MagicMock()
    game_version.canonical_json = valid_canonical_json
    game_version.engine_version = "runtime-core@1.8.0"

    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.commit = AsyncMock()
    factory = MagicMock(return_value=session)

    with patch(
        "app.distributed.orchestration_service.SimulationRepository",
    ) as sim_repo_cls, patch(
        "app.distributed.orchestration_service.GameVersionRepository",
    ) as gv_repo_cls, patch(
        "app.distributed.orchestration_service.SimulationShardRepository",
    ) as shard_repo_cls, patch(
        "app.distributed.orchestration_service.assign_shards",
        return_value=[
            MagicMock(shard_index=0, spin_count=0),
            MagicMock(shard_index=1, spin_count=3),
        ],
    ):
        sim_repo_cls.return_value.get_by_id = AsyncMock(return_value=simulation)
        gv_repo_cls.return_value.get_by_id = AsyncMock(return_value=game_version)
        shard_repo_cls.return_value.add = AsyncMock()

        service = OrchestrationService(
            factory,
            Settings(simulation_shard_min=2, simulation_shard_max=2),
        )
        created = await service.prepare_shards(simulation_id)
        assert len(created) == 1


@pytest.mark.asyncio
async def test_shard_service_noop_paths() -> None:
    simulation_id = uuid.uuid4()
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    factory = MagicMock(return_value=session)

    with patch(
        "app.distributed.shard_service.SimulationShardRepository",
    ) as shard_repo_cls, patch(
        "app.distributed.shard_service.SimulationRepository",
    ) as sim_repo_cls:
        shard_repo = AsyncMock()
        shard_repo.get_by_simulation_and_index.return_value = None
        shard_repo_cls.return_value = shard_repo
        sim_repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        service = ShardService(factory)
        await service.mark_running(simulation_id, 0, worker_id="w")
        assert await service.mark_completed(
            simulation_id,
            0,
            partial=PartialAccumulator(spin_count=1, total_bet_minor_units=100),
        ) is None
        assert await service.mark_failed(simulation_id, 0, error_message="x") is None


@pytest.mark.asyncio
async def test_shard_service_mark_completed_missing_simulation() -> None:
    simulation_id = uuid.uuid4()
    shard = MagicMock()
    shard.spin_count = 5

    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.commit = AsyncMock()
    factory = MagicMock(return_value=session)

    with patch(
        "app.distributed.shard_service.SimulationShardRepository",
    ) as shard_repo_cls, patch(
        "app.distributed.shard_service.SimulationRepository",
    ) as sim_repo_cls:
        shard_repo_cls.return_value.get_by_simulation_and_index = AsyncMock(
            return_value=shard,
        )
        sim_repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        service = ShardService(factory)
        assert (
            await service.mark_completed(
                simulation_id,
                0,
                partial=PartialAccumulator(spin_count=5, total_bet_minor_units=500),
            )
            is None
        )


@pytest.mark.asyncio
async def test_shard_service_mark_running_sets_pending_to_running() -> None:
    simulation_id = uuid.uuid4()
    shard = MagicMock()
    simulation = Simulation(
        id=simulation_id,
        game_version_id=uuid.uuid4(),
        spin_count=10,
        completed_spin_count=0,
        bet_minor_units=100,
        status=SimulationStatus.PENDING,
    )

    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.commit = AsyncMock()
    factory = MagicMock(return_value=session)

    with patch(
        "app.distributed.shard_service.SimulationShardRepository",
    ) as shard_repo_cls, patch(
        "app.distributed.shard_service.SimulationRepository",
    ) as sim_repo_cls:
        shard_repo_cls.return_value.get_by_simulation_and_index = AsyncMock(
            return_value=shard,
        )
        sim_repo_cls.return_value.get_by_id = AsyncMock(return_value=simulation)

        service = ShardService(factory)
        await service.mark_running(simulation_id, 0, worker_id="worker-1")
        assert simulation.status == SimulationStatus.RUNNING


def test_refresh_progress_zero_shards() -> None:
    simulation = Simulation(
        id=uuid.uuid4(),
        game_version_id=uuid.uuid4(),
        spin_count=10,
        completed_spin_count=0,
        bet_minor_units=100,
        total_shards=0,
    )
    ShardService._refresh_progress(simulation)
    assert simulation.progress_percentage == 0.0


@pytest.mark.asyncio
async def test_run_shard_async_missing_simulation() -> None:
    simulation_id = uuid.uuid4()
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    factory = MagicMock(return_value=session)

    with patch("app.distributed.tasks._session_factory", return_value=factory), patch(
        "app.distributed.tasks.SimulationRepository",
    ) as sim_repo_cls:
        sim_repo_cls.return_value.get_by_id = AsyncMock(return_value=None)
        result = await _run_shard_async(
            simulation_id,
            0,
            worker_id="w",
            celery_task_id="t",
        )
        assert result == "missing"


@pytest.mark.asyncio
async def test_run_shard_async_cancelled_after_running(
    valid_canonical_json: dict,
) -> None:
    simulation_id = uuid.uuid4()
    simulation = MagicMock()
    simulation.cancel_requested = False

    cancelled = MagicMock()
    cancelled.cancel_requested = True

    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    factory = MagicMock(return_value=session)

    get_by_id = AsyncMock(side_effect=[simulation, cancelled])
    with patch("app.distributed.tasks._session_factory", return_value=factory), patch(
        "app.distributed.tasks.SimulationRepository",
    ) as sim_repo_cls, patch(
        "app.distributed.tasks.ShardService",
    ) as shard_cls:
        sim_repo_cls.return_value.get_by_id = get_by_id
        shard_cls.return_value.mark_running = AsyncMock()
        shard_cls.return_value.mark_cancelled_shards = AsyncMock()

        result = await _run_shard_async(
            simulation_id,
            0,
            worker_id="w",
            celery_task_id="t",
        )
        assert result == "cancelled"
