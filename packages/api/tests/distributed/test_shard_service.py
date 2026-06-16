"""Shard service tests."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.db.models.simulation import Simulation, SimulationStatus
from app.db.models.simulation_shard import SimulationShardStatus
from app.distributed.shard_service import ShardService
from runtime_core.simulation import PartialAccumulator


@pytest.mark.asyncio
async def test_shard_service_refresh_progress() -> None:
    simulation = Simulation(
        id=uuid.uuid4(),
        game_version_id=uuid.uuid4(),
        spin_count=100,
        completed_spin_count=0,
        bet_minor_units=100,
        total_shards=4,
        completed_shards=2,
        failed_shards=1,
    )
    ShardService._refresh_progress(simulation)
    assert simulation.progress_percentage == 75.0


@pytest.mark.asyncio
async def test_mark_completed_updates_simulation() -> None:
    simulation_id = uuid.uuid4()
    shard = MagicMock()
    shard.spin_count = 10
    shard.status = SimulationShardStatus.RUNNING

    simulation = Simulation(
        id=simulation_id,
        game_version_id=uuid.uuid4(),
        spin_count=40,
        completed_spin_count=0,
        bet_minor_units=100,
        status=SimulationStatus.RUNNING,
        total_shards=4,
        completed_shards=0,
        failed_shards=0,
    )

    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    factory = MagicMock(return_value=session)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "app.distributed.shard_service.SimulationShardRepository",
            lambda s: AsyncMock(
                get_by_simulation_and_index=AsyncMock(return_value=shard),
            ),
        )
        mp.setattr(
            "app.distributed.shard_service.SimulationRepository",
            lambda s: AsyncMock(get_by_id=AsyncMock(return_value=simulation)),
        )
        service = ShardService(factory)
        result = await service.mark_completed(
            simulation_id,
            0,
            partial=PartialAccumulator(spin_count=10, total_bet_minor_units=1000),
        )
        assert result is not None
        assert simulation.completed_shards == 1
