"""Integration tests for simulation execution at scale."""

from __future__ import annotations

import asyncio
import os
import uuid

import pytest
from runtime_core.common.golden import load_golden_game_version
from runtime_core.runtime.events import EventLogMode

from app.adapters.simulation import build_simulation_profile
from app.adapters.simulation_runner import execute_simulation_async
from app.config import Settings
from app.exceptions.simulation import SimulationJobCancelledError
from app.jobs.process_pool import SimulationProcessPool


@pytest.fixture
def golden_game():
    return load_golden_game_version("fixture-01-base-5x3")


@pytest.fixture
def integration_pool() -> SimulationProcessPool:
    pool = SimulationProcessPool(max_workers=2)
    pool.start()
    yield pool
    pool.shutdown(wait=True)


@pytest.fixture
def integration_settings() -> Settings:
    return Settings(
        simulation_process_pool_workers=2,
        simulation_spin_wins_detail_limit=0,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("spin_count", [10_000, 100_000, 1_000_000])
async def test_sharded_simulation_completes_at_scale(
    golden_game,
    integration_pool,
    integration_settings,
    spin_count: int,
) -> None:
    if spin_count >= 100_000 and os.getenv("RUN_SIM_INTEGRATION") != "1":
        pytest.skip("Set RUN_SIM_INTEGRATION=1 to run large spin integration tests")

    simulation_id = uuid.uuid4()
    profile = build_simulation_profile(
        simulation_id=simulation_id,
        spin_count=spin_count,
        bet_minor_units=100,
        event_log_mode=EventLogMode.NONE,
        master_seed="integration-scale",
        engine_version="runtime-core@1.8.0",
    )
    progress_updates: list[tuple[int, int]] = []

    outcome = await execute_simulation_async(
        golden_game,
        profile,
        simulation_id=simulation_id,
        process_pool=integration_pool.executor(),
        on_progress=lambda completed, total: progress_updates.append((completed, total)),
        spin_wins_detail_limit=integration_settings.simulation_spin_wins_detail_limit,
    )

    assert outcome.engine_result.spin_count == spin_count
    assert progress_updates
    assert progress_updates[-1] == (spin_count, spin_count)


@pytest.mark.asyncio
async def test_cancellation_stops_between_shards(
    golden_game,
    integration_pool,
) -> None:
    simulation_id = uuid.uuid4()
    profile = build_simulation_profile(
        simulation_id=simulation_id,
        spin_count=20_000,
        bet_minor_units=100,
        event_log_mode=EventLogMode.NONE,
        master_seed="cancel-test",
        engine_version="runtime-core@1.8.0",
        shard_count=20,
    )
    cancelled = False

    def should_cancel() -> bool:
        return cancelled

    def on_shard_completed(shard_index: int, completed: int, total: int) -> None:
        del shard_index, completed, total
        nonlocal cancelled
        cancelled = True

    with pytest.raises(SimulationJobCancelledError):
        await execute_simulation_async(
            golden_game,
            profile,
            simulation_id=simulation_id,
            process_pool=integration_pool.executor(),
            should_cancel=should_cancel,
            on_shard_completed=on_shard_completed,
            spin_wins_detail_limit=0,
        )
