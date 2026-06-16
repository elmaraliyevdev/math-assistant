"""Additional distributed module tests for coverage."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.config import Settings
from app.db.models.simulation import Simulation, SimulationStatus
from app.db.models.simulation_shard import SimulationShardStatus
from app.distributed.aggregation_service import AggregationService, merge_partials
from app.distributed.monitoring_service import MonitoringService
from app.distributed.queue import DistributedSimulationQueue
from app.distributed.tasks import _orchestrate_async
from app.jobs.models import SimulationJob
from runtime_core.simulation import PartialAccumulator


@pytest.mark.asyncio
async def test_distributed_queue_enqueue() -> None:
    queue = DistributedSimulationQueue()
    with patch("app.distributed.tasks.orchestrate_simulation") as task:
        task.delay.return_value = MagicMock(id="task-1")
        await queue.enqueue(SimulationJob(simulation_id=uuid.uuid4()))
        task.delay.assert_called_once()


def test_merge_partials_empty() -> None:
    merged = merge_partials([PartialAccumulator.empty()])
    assert merged.spin_count == 0


@pytest.mark.asyncio
async def test_aggregation_finalize_cancelled() -> None:
    simulation_id = uuid.uuid4()
    simulation = Simulation(
        id=simulation_id,
        game_version_id=uuid.uuid4(),
        spin_count=10,
        completed_spin_count=0,
        bet_minor_units=100,
        status=SimulationStatus.RUNNING,
        cancel_requested=True,
        total_shards=1,
    )
    shard = MagicMock()
    shard.status = SimulationShardStatus.CANCELLED

    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.commit = AsyncMock()

    factory = MagicMock(return_value=session)

    with patch(
        "app.distributed.aggregation_service.SimulationRepository",
    ) as sim_repo_cls, patch(
        "app.distributed.aggregation_service.SimulationShardRepository",
    ) as shard_repo_cls:
        sim_repo = AsyncMock()
        sim_repo.get_by_id.return_value = simulation
        sim_repo_cls.return_value = sim_repo
        shard_repo = AsyncMock()
        shard_repo.list_by_simulation_id.return_value = [shard]
        shard_repo_cls.return_value = shard_repo

        service = AggregationService(factory, Settings())
        assert await service.try_finalize(simulation_id) is True
        assert simulation.status == SimulationStatus.FAILED


def test_monitoring_workers_with_stats() -> None:
    monitoring = MonitoringService(session_factory=MagicMock())
    with patch("app.distributed.celery_app.celery_app") as celery:
        celery.control.inspect.return_value.active.return_value = {
            "worker@host": [{"id": "1"}],
        }
        celery.control.inspect.return_value.stats.return_value = {
            "worker@host": {"total": {"tasks.simulation": 3}},
        }
        workers = monitoring.list_workers()
        assert workers.active_workers == 1
        assert workers.items[0].active_tasks == 1


@pytest.mark.asyncio
async def test_orchestrate_async_no_simulation() -> None:
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.commit = AsyncMock()
    factory = MagicMock(return_value=session)

    with patch(
        "app.distributed.tasks._session_factory",
        return_value=factory,
    ), patch(
        "app.distributed.tasks.OrchestrationService",
    ) as orch_cls:
        orch = AsyncMock()
        orch.prepare_shards.return_value = []
        orch_cls.return_value = orch
        result = await _orchestrate_async(uuid.uuid4())
        assert result == 0
