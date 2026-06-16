"""Final coverage gaps for distributed package."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.config import Settings
from app.db.models.simulation import Simulation, SimulationStatus
from app.distributed.aggregation_service import AggregationService
from app.distributed.celery_app import celery_app
from app.distributed.monitoring_service import MonitoringService
from app.distributed.orchestration_service import OrchestrationService
from app.distributed.shard_service import ShardService
from app.distributed.worker_service import execute_simulation_shard


def test_celery_eager_configuration() -> None:
    settings = Settings(celery_task_always_eager=True)
    assert settings.celery_task_always_eager is True
    celery_app.conf.task_always_eager = True
    assert celery_app.conf.task_always_eager is True


@pytest.mark.asyncio
async def test_aggregation_skips_completed_simulation() -> None:
    simulation = Simulation(
        id=uuid.uuid4(),
        game_version_id=uuid.uuid4(),
        spin_count=1,
        completed_spin_count=1,
        bet_minor_units=100,
        status=SimulationStatus.COMPLETED,
    )
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    factory = MagicMock(return_value=session)

    with patch(
        "app.distributed.aggregation_service.SimulationRepository",
    ) as sim_repo_cls:
        sim_repo = AsyncMock()
        sim_repo.get_by_id.return_value = simulation
        sim_repo_cls.return_value = sim_repo
        service = AggregationService(factory, Settings())
        assert await service.try_finalize(simulation.id) is False


@pytest.mark.asyncio
async def test_prepare_shards_missing_simulation() -> None:
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    factory = MagicMock(return_value=session)

    with patch(
        "app.distributed.orchestration_service.SimulationRepository",
    ) as sim_repo_cls:
        sim_repo = AsyncMock()
        sim_repo.get_by_id.return_value = None
        sim_repo_cls.return_value = sim_repo
        service = OrchestrationService(factory, Settings())
        assert await service.prepare_shards(uuid.uuid4()) == []


def test_execute_simulation_shard_empty_assignment(valid_canonical_json: dict) -> None:
    partial = execute_simulation_shard(
        simulation_id=uuid.uuid4(),
        game_canonical_json=valid_canonical_json,
        spin_count=20,
        bet_minor_units=100,
        event_log_mode="none",
        master_seed="seed",
        engine_version="runtime-core@1.8.0",
        shard_index=99,
        total_shard_count=4,
    )
    assert partial.spin_count == 0


@pytest.mark.asyncio
async def test_prepare_shards_missing_game_version() -> None:
    simulation_id = uuid.uuid4()
    simulation = Simulation(
        id=simulation_id,
        game_version_id=uuid.uuid4(),
        spin_count=10,
        completed_spin_count=0,
        bet_minor_units=100,
        status=SimulationStatus.PENDING,
        event_log_mode="none",
    )
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    factory = MagicMock(return_value=session)

    with patch(
        "app.distributed.orchestration_service.SimulationRepository",
    ) as sim_repo_cls, patch(
        "app.distributed.orchestration_service.GameVersionRepository",
    ) as gv_repo_cls:
        sim_repo = AsyncMock()
        sim_repo.get_by_id.return_value = simulation
        sim_repo_cls.return_value = sim_repo
        gv_repo = AsyncMock()
        gv_repo.get_by_id.return_value = None
        gv_repo_cls.return_value = gv_repo
        service = OrchestrationService(factory, Settings())
        assert await service.prepare_shards(simulation_id) == []


@pytest.mark.asyncio
async def test_shard_service_list_shards() -> None:
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    factory = MagicMock(return_value=session)
    with patch(
        "app.distributed.shard_service.SimulationShardRepository",
    ) as repo_cls:
        repo = AsyncMock()
        repo.list_by_simulation_id.return_value = []
        repo_cls.return_value = repo
        service = ShardService(factory)
        assert await service.list_shards(uuid.uuid4()) == []


def test_distributed_queue_pending_count() -> None:
    from app.distributed.queue import DistributedSimulationQueue

    assert DistributedSimulationQueue().pending_count == 0


@pytest.mark.asyncio
async def test_monitoring_reserved_exception() -> None:
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.scalar = AsyncMock(return_value=0)
    session.execute = AsyncMock(return_value=MagicMock(all=MagicMock(return_value=[])))
    monitoring = MonitoringService(MagicMock(return_value=session))

    with patch("app.distributed.celery_app.celery_app") as celery:
        celery.control.inspect.side_effect = RuntimeError("no workers")
        summary = await monitoring.queue_summary()
        assert summary.pending_tasks == 0
