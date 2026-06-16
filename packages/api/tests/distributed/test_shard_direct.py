"""Shard service direct coverage tests."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.db.models.simulation import Simulation, SimulationStatus
from app.db.models.simulation_shard import SimulationShard, SimulationShardStatus
from app.distributed.shard_service import ShardService
from runtime_core.simulation import PartialAccumulator


@pytest.mark.asyncio
async def test_mark_running_starts_simulation() -> None:
    simulation_id = uuid.uuid4()
    shard = SimulationShard(
        simulation_id=simulation_id,
        shard_index=0,
        spin_count=5,
        status=SimulationShardStatus.PENDING,
    )
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
        shard_repo = AsyncMock()
        shard_repo.get_by_simulation_and_index.return_value = shard
        shard_repo_cls.return_value = shard_repo
        sim_repo = AsyncMock()
        sim_repo.get_by_id.return_value = simulation
        sim_repo_cls.return_value = sim_repo

        service = ShardService(factory)
        await service.mark_running(simulation_id, 0, worker_id="worker-1")
        assert shard.status == SimulationShardStatus.RUNNING
        assert simulation.status == SimulationStatus.RUNNING


@pytest.mark.asyncio
async def test_mark_completed_updates_progress() -> None:
    simulation_id = uuid.uuid4()
    shard = SimulationShard(
        simulation_id=simulation_id,
        shard_index=0,
        spin_count=5,
        status=SimulationShardStatus.RUNNING,
    )
    simulation = Simulation(
        id=simulation_id,
        game_version_id=uuid.uuid4(),
        spin_count=10,
        completed_spin_count=0,
        bet_minor_units=100,
        status=SimulationStatus.RUNNING,
        total_shards=2,
        completed_shards=0,
        failed_shards=0,
    )

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
        shard_repo.get_by_simulation_and_index.return_value = shard
        shard_repo_cls.return_value = shard_repo
        sim_repo = AsyncMock()
        sim_repo.get_by_id.return_value = simulation
        sim_repo_cls.return_value = sim_repo

        service = ShardService(factory)
        result = await service.mark_completed(
            simulation_id,
            0,
            partial=PartialAccumulator(spin_count=5, total_bet_minor_units=500),
        )
        assert result is not None
        assert simulation.completed_shards == 1
