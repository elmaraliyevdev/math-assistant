"""Task and orchestration edge-case coverage."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.config import Settings
from app.distributed.orchestration_service import OrchestrationService
from app.distributed.shard_service import ShardService
from app.distributed.tasks import _orchestrate_async, _run_async, _run_shard_async


@pytest.mark.asyncio
async def test_run_async_from_running_loop_wrapper() -> None:
    async def sample() -> str:
        return "ok"

    assert _run_async(sample()) == "ok"


@pytest.mark.asyncio
async def test_orchestrate_async_dispatches(valid_canonical_json: dict) -> None:
    simulation_id = uuid.uuid4()
    with patch("app.distributed.tasks._session_factory") as factory, patch(
        "app.distributed.tasks.OrchestrationService",
    ) as orch_cls:
        orch = AsyncMock()
        orch.prepare_shards.return_value = [MagicMock()]
        orch.dispatch_shards.return_value = 2
        orch_cls.return_value = orch
        factory.return_value = MagicMock()
        result = await _orchestrate_async(simulation_id)
        assert result == 2


@pytest.mark.asyncio
async def test_run_shard_async_missing_game_version(valid_canonical_json: dict) -> None:
    simulation_id = uuid.uuid4()
    simulation = MagicMock()
    simulation.cancel_requested = False
    simulation.game_version_id = uuid.uuid4()

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
        gv_repo_cls.return_value.get_by_id = AsyncMock(return_value=None)
        shard_cls.return_value.mark_running = AsyncMock()
        shard_cls.return_value.mark_failed = AsyncMock()
        agg_cls.return_value.try_finalize = AsyncMock(return_value=False)

        result = await _run_shard_async(
            simulation_id,
            0,
            worker_id="w",
            celery_task_id="t",
        )
        assert result == "failed"


@pytest.mark.asyncio
async def test_orchestrate_empty_prepare() -> None:
    session = MagicMock()
    factory = MagicMock(return_value=session)
    with patch("app.distributed.tasks._session_factory", return_value=factory), patch(
        "app.distributed.tasks.OrchestrationService",
    ) as orch_cls:
        orch = AsyncMock()
        orch.prepare_shards.return_value = []
        orch_cls.return_value = orch
        assert await _orchestrate_async(uuid.uuid4()) == 0


@pytest.mark.asyncio
async def test_run_shard_async_cancelled() -> None:
    simulation_id = uuid.uuid4()
    simulation = MagicMock()
    simulation.cancel_requested = True

    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    factory = MagicMock(return_value=session)

    with patch("app.distributed.tasks._session_factory", return_value=factory), patch(
        "app.distributed.tasks.SimulationRepository",
    ) as sim_repo_cls, patch(
        "app.distributed.tasks.ShardService",
    ) as shard_cls:
        sim_repo_cls.return_value.get_by_id = AsyncMock(return_value=simulation)
        shard_cls.return_value.mark_cancelled_shards = AsyncMock()

        result = await _run_shard_async(
            simulation_id,
            0,
            worker_id="w",
            celery_task_id="t",
        )
        assert result == "cancelled"


@pytest.mark.asyncio
async def test_run_shard_async_handles_exception(valid_canonical_json: dict) -> None:
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
    ) as agg_cls, patch(
        "app.distributed.tasks.execute_simulation_shard",
        side_effect=RuntimeError("boom"),
    ):
        sim_repo_cls.return_value.get_by_id = AsyncMock(return_value=simulation)
        gv_repo_cls.return_value.get_by_id = AsyncMock(return_value=game_version)
        shard_cls.return_value.mark_running = AsyncMock()
        shard_cls.return_value.mark_failed = AsyncMock()
        agg_cls.return_value.try_finalize = AsyncMock(return_value=False)

        result = await _run_shard_async(
            simulation_id,
            0,
            worker_id="w",
            celery_task_id="t",
        )
        assert result == "done"
