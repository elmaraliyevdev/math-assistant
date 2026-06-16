"""Worker service and task execution tests."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.distributed.tasks import _run_async, _run_shard_async
from app.distributed.worker_service import execute_simulation_shard


def test_execute_simulation_shard_returns_accumulator(valid_canonical_json: dict) -> None:
    simulation_id = uuid.uuid4()
    partial = execute_simulation_shard(
        simulation_id=simulation_id,
        game_canonical_json=valid_canonical_json,
        spin_count=20,
        bet_minor_units=100,
        event_log_mode="none",
        master_seed="shard-test",
        engine_version="runtime-core@1.8.0",
        shard_index=0,
        total_shard_count=4,
    )
    assert partial.spin_count > 0


def test_run_async_without_running_loop() -> None:
    async def sample() -> int:
        return 42

    assert _run_async(sample()) == 42


@pytest.mark.asyncio
async def test_run_shard_async_completes_shard(valid_canonical_json: dict) -> None:
    simulation_id = uuid.uuid4()
    simulation = MagicMock()
    simulation.cancel_requested = False
    simulation.game_version_id = uuid.uuid4()
    simulation.spin_count = 20
    simulation.bet_minor_units = 100
    simulation.event_log_mode = "none"
    simulation.master_seed = "seed"
    simulation.total_shards = 4

    game_version = MagicMock()
    game_version.canonical_json = valid_canonical_json
    game_version.engine_version = "runtime-core@1.8.0"

    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    factory = MagicMock(return_value=session)

    with patch("app.distributed.tasks._session_factory", return_value=factory), patch(
        "app.distributed.tasks.SimulationRepository",
    ) as sim_repo_cls, patch(
        "app.distributed.tasks.GameVersionRepository",
    ) as gv_repo_cls, patch(
        "app.distributed.tasks.ShardService",
    ) as shard_cls, patch(
        "app.distributed.tasks.AggregationService",
    ) as agg_cls:
        sim_repo_cls.return_value.get_by_id = AsyncMock(return_value=simulation)
        gv_repo_cls.return_value.get_by_id = AsyncMock(return_value=game_version)
        shard_cls.return_value.mark_running = AsyncMock()
        shard_cls.return_value.mark_completed = AsyncMock()
        agg_cls.return_value.try_finalize = AsyncMock(return_value=True)

        result = await _run_shard_async(
            simulation_id,
            0,
            worker_id="worker-1",
            celery_task_id="task-1",
        )
        assert result == "done"
