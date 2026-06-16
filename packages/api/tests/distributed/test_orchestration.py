"""Distributed orchestration unit tests."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.config import Settings
from app.db.models.simulation_shard import SimulationShardStatus
from app.distributed.orchestration_service import OrchestrationService


@pytest.mark.asyncio
async def test_compute_shard_count_uses_settings() -> None:
    service = OrchestrationService(AsyncMock(), Settings(simulation_spins_per_shard=500))
    assert service.compute_shard_count_for(2000) == 4


@pytest.mark.asyncio
async def test_dispatch_shards_enqueues_tasks() -> None:
    simulation_id = uuid.uuid4()
    shard = MagicMock()
    shard.shard_index = 0
    shard.status = SimulationShardStatus.PENDING

    session = AsyncMock()

    async def session_ctx():
        return session

    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)

    def factory():
        return session

    with patch("app.distributed.orchestration_service.SimulationShardRepository") as repo_cls:
        repo = AsyncMock()
        repo.list_by_simulation_id.return_value = [shard]
        repo.get_by_simulation_and_index.return_value = shard
        repo_cls.return_value = repo

        with patch("app.distributed.tasks.run_simulation_shard") as task:
            task.delay.return_value = MagicMock(id="task-1")
            service = OrchestrationService(factory, Settings())
            count = await service.dispatch_shards(simulation_id)
            assert count == 1
            task.delay.assert_called_once()
