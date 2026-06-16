"""Aggregation failure-path tests."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.config import Settings
from app.db.models.simulation import Simulation, SimulationStatus
from app.db.models.simulation_shard import SimulationShardStatus
from app.distributed.aggregation_service import AggregationService


@pytest.mark.asyncio
async def test_aggregation_marks_failed_when_shard_failed() -> None:
    simulation_id = uuid.uuid4()
    simulation = Simulation(
        id=simulation_id,
        game_version_id=uuid.uuid4(),
        spin_count=10,
        completed_spin_count=0,
        bet_minor_units=100,
        status=SimulationStatus.RUNNING,
        total_shards=1,
    )
    shard = MagicMock()
    shard.status = SimulationShardStatus.FAILED
    shard.error_message = "shard boom"

    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.commit = AsyncMock()
    factory = MagicMock(return_value=session)

    with patch(
        "app.distributed.aggregation_service.SimulationRepository",
    ) as sim_repo_cls, patch(
        "app.distributed.aggregation_service.SimulationShardRepository",
    ) as shard_repo_cls, patch(
        "app.distributed.aggregation_service.notify_simulation_finished_by_id",
        new_callable=AsyncMock,
    ):
        sim_repo = AsyncMock()
        sim_repo.get_by_id.return_value = simulation
        sim_repo_cls.return_value = sim_repo
        shard_repo = AsyncMock()
        shard_repo.list_by_simulation_id.return_value = [shard]
        shard_repo_cls.return_value = shard_repo

        service = AggregationService(factory, Settings())
        assert await service.try_finalize(simulation_id) is True
        assert simulation.status == SimulationStatus.FAILED


@pytest.mark.asyncio
async def test_aggregation_missing_game_version() -> None:
    simulation_id = uuid.uuid4()
    simulation = Simulation(
        id=simulation_id,
        game_version_id=uuid.uuid4(),
        spin_count=10,
        completed_spin_count=10,
        bet_minor_units=100,
        status=SimulationStatus.RUNNING,
        event_log_mode="none",
        master_seed="seed",
        total_shards=1,
        completed_shards=1,
    )
    shard = MagicMock()
    shard.status = SimulationShardStatus.COMPLETED
    shard.partial_result = {"spin_count": 10, "total_bet_minor_units": 1000, "total_win_minor_units": 100}

    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.commit = AsyncMock()
    factory = MagicMock(return_value=session)

    with patch(
        "app.distributed.aggregation_service.SimulationRepository",
    ) as sim_repo_cls, patch(
        "app.distributed.aggregation_service.SimulationShardRepository",
    ) as shard_repo_cls, patch(
        "app.distributed.aggregation_service.GameVersionRepository",
    ) as gv_repo_cls:
        sim_repo = AsyncMock()
        sim_repo.get_by_id.return_value = simulation
        sim_repo_cls.return_value = sim_repo
        shard_repo = AsyncMock()
        shard_repo.list_by_simulation_id.return_value = [shard]
        shard_repo_cls.return_value = shard_repo
        gv_repo = AsyncMock()
        gv_repo.get_by_id.return_value = None
        gv_repo_cls.return_value = gv_repo

        service = AggregationService(factory, Settings())
        assert await service.try_finalize(simulation_id) is True
        assert simulation.status == SimulationStatus.FAILED
