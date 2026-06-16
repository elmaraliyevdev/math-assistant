"""Benchmark simulation job execution infrastructure."""

from __future__ import annotations

import os
import time
import uuid

import pytest
from runtime_core.common.golden import load_golden_game_version
from runtime_core.runtime.events import EventLogMode

from app.adapters.simulation import build_simulation_profile
from app.adapters.simulation_runner import execute_simulation_async
from app.jobs.process_pool import SimulationProcessPool


@pytest.mark.asyncio
@pytest.mark.parametrize("spin_count", [10_000, 100_000, 1_000_000])
async def test_simulation_execution_benchmark(spin_count: int) -> None:
    if os.getenv("RUN_SIM_BENCHMARK") != "1":
        pytest.skip("Set RUN_SIM_BENCHMARK=1 to run simulation benchmarks")

    game = load_golden_game_version("fixture-01-base-5x3")
    pool = SimulationProcessPool(max_workers=2)
    pool.start()
    simulation_id = uuid.uuid4()
    profile = build_simulation_profile(
        simulation_id=simulation_id,
        spin_count=spin_count,
        bet_minor_units=100,
        event_log_mode=EventLogMode.NONE,
        master_seed="benchmark",
        engine_version="runtime-core@1.8.0",
    )
    progress_updates: list[tuple[int, int]] = []
    started = time.perf_counter()

    outcome = await execute_simulation_async(
        game,
        profile,
        simulation_id=simulation_id,
        process_pool=pool.executor(),
        on_progress=lambda completed, total: progress_updates.append((completed, total)),
        spin_wins_detail_limit=0,
    )

    elapsed = time.perf_counter() - started
    pool.shutdown(wait=True)

    print(
        f"\n[benchmark] spins={spin_count} "
        f"elapsed_s={elapsed:.2f} "
        f"progress_events={len(progress_updates)} "
        f"shards={profile.shard_count} "
        f"pool_workers={pool.max_workers}",
    )
    assert outcome.engine_result.spin_count == spin_count
    assert len(progress_updates) == profile.shard_count
