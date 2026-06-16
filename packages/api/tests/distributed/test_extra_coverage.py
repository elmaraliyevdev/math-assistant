"""Additional coverage for distributed helpers."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.config import Settings
from app.db.models.simulation_shard import SimulationShard, SimulationShardStatus
from app.distributed.orchestration_service import OrchestrationService
from app.distributed.queue import DistributedSimulationQueue
from app.distributed.shard_service import ShardService


@pytest.mark.asyncio
async def test_retry_failed_dispatches() -> None:
    simulation_id = uuid.uuid4()
    shard = SimulationShard(
        simulation_id=simulation_id,
        shard_index=1,
        spin_count=10,
        status=SimulationShardStatus.PENDING,
    )

    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.commit = AsyncMock()
    factory = MagicMock(return_value=session)

    with patch(
        "app.distributed.shard_service.ShardService.reset_failed_shards",
        new_callable=AsyncMock,
        return_value=[shard],
    ), patch(
        "app.distributed.tasks.run_simulation_shard",
    ) as task, patch(
        "app.distributed.orchestration_service.SimulationShardRepository",
    ) as repo_cls:
        repo = AsyncMock()
        repo.get_by_simulation_and_index.return_value = shard
        repo_cls.return_value = repo
        task.delay.return_value = MagicMock(id="task-2")

        service = OrchestrationService(factory, Settings())
        count = await service.retry_failed(simulation_id)
        assert count == 1


@pytest.mark.asyncio
async def test_shard_service_reset_and_cancel() -> None:
    simulation_id = uuid.uuid4()
    shard = SimulationShard(
        simulation_id=simulation_id,
        shard_index=0,
        spin_count=10,
        status=SimulationShardStatus.RUNNING,
        celery_task_id="task-x",
    )

    simulation = MagicMock()
    simulation.failed_shards = 1
    simulation.total_shards = 2
    simulation.completed_shards = 1

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
        shard_repo = AsyncMock()
        shard_repo.list_failed.return_value = [shard]
        shard_repo.list_by_simulation_id.return_value = [shard]
        shard_repo_cls.return_value = shard_repo
        sim_repo = AsyncMock()
        sim_repo.get_by_id.return_value = simulation
        sim_repo_cls.return_value = sim_repo

        service = ShardService(factory)
        task_ids = await service.mark_cancelled_shards(simulation_id)
        assert task_ids == ["task-x"]
        reset = await service.reset_failed_shards(simulation_id)
        assert len(reset) == 1


@pytest.mark.asyncio
async def test_queue_dequeue_not_supported() -> None:
    queue = DistributedSimulationQueue()
    with pytest.raises(NotImplementedError):
        await queue.dequeue()
