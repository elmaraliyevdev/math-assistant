"""Orchestration and aggregation integration-style unit tests."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.config import Settings
from app.db.models.simulation import Simulation, SimulationStatus
from app.db.models.simulation_shard import SimulationShard, SimulationShardStatus
from app.distributed.aggregation_service import AggregationService
from app.distributed.orchestration_service import OrchestrationService
from app.distributed.shard_service import ShardService
from runtime_core.simulation import PartialAccumulator


@pytest.mark.asyncio
async def test_prepare_shards_persists_rows() -> None:
    simulation_id = uuid.uuid4()
    simulation = Simulation(
        id=simulation_id,
        game_version_id=uuid.uuid4(),
        spin_count=40,
        completed_spin_count=0,
        bet_minor_units=100,
        status=SimulationStatus.PENDING,
        event_log_mode="none",
        master_seed="seed",
    )
    game_version = MagicMock()
    game_version.engine_version = "runtime-core@1.8.0"

    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.commit = AsyncMock()

    factory = MagicMock(return_value=session)

    with patch(
        "app.distributed.orchestration_service.SimulationRepository",
    ) as sim_repo_cls, patch(
        "app.distributed.orchestration_service.SimulationShardRepository",
    ) as shard_repo_cls, patch(
        "app.distributed.orchestration_service.GameVersionRepository",
    ) as gv_repo_cls:
        sim_repo = AsyncMock()
        sim_repo.get_by_id.return_value = simulation
        sim_repo_cls.return_value = sim_repo
        shard_repo = AsyncMock()
        shard_repo.add = AsyncMock(side_effect=lambda entity: entity)
        shard_repo_cls.return_value = shard_repo
        gv_repo = AsyncMock()
        gv_repo.get_by_id.return_value = game_version
        gv_repo_cls.return_value = gv_repo

        service = OrchestrationService(factory, Settings())
        shards = await service.prepare_shards(simulation_id)
        assert len(shards) >= 1
        assert simulation.distributed_execution is True
        assert simulation.total_shards == len(shards)


@pytest.mark.asyncio
async def test_aggregation_completes_simulation(valid_canonical_json: dict) -> None:
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
        failed_shards=0,
    )
    from app.distributed.accumulator_codec import partial_accumulator_to_dict

    shard = MagicMock()
    shard.status = SimulationShardStatus.COMPLETED
    shard.partial_result = partial_accumulator_to_dict(
        PartialAccumulator(
            spin_count=10,
            total_bet_minor_units=1000,
            total_win_minor_units=400,
        ),
    )

    game_version = MagicMock()
    game_version.engine_version = "runtime-core@1.8.0"
    game_version.canonical_json = valid_canonical_json

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
    ) as gv_repo_cls, patch(
        "app.distributed.aggregation_service.SimulationResultRepository",
    ) as result_repo_cls, patch(
        "app.distributed.aggregation_service.notify_simulation_finished_by_id",
        new_callable=AsyncMock,
    ), patch(
        "app.distributed.aggregation_service.enrich_mathematics_report",
        side_effect=lambda report, **_: report,
    ):
        sim_repo = AsyncMock()
        sim_repo.get_by_id.return_value = simulation
        sim_repo_cls.return_value = sim_repo
        shard_repo = AsyncMock()
        shard_repo.list_by_simulation_id.return_value = [shard]
        shard_repo_cls.return_value = shard_repo
        gv_repo = AsyncMock()
        gv_repo.get_by_id.return_value = game_version
        gv_repo_cls.return_value = gv_repo
        result_repo = AsyncMock()
        result_repo.add = AsyncMock()
        result_repo_cls.return_value = result_repo

        service = AggregationService(factory, Settings())
        assert await service.try_finalize(simulation_id) is True
        assert simulation.status == SimulationStatus.COMPLETED


@pytest.mark.asyncio
async def test_shard_service_mark_failed() -> None:
    simulation_id = uuid.uuid4()
    shard = MagicMock()
    simulation = Simulation(
        id=simulation_id,
        game_version_id=uuid.uuid4(),
        spin_count=10,
        completed_spin_count=0,
        bet_minor_units=100,
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
        result = await service.mark_failed(simulation_id, 0, error_message="boom")
        assert result is not None
        assert simulation.failed_shards == 1
