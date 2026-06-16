"""Benchmark fixture loading (read-only golden access)."""

from __future__ import annotations

from runtime_core.common.golden import load_golden_game_version
from runtime_core.domain.game_version import GameVersion
from runtime_core.simulation.models import SimulationProfile

from benchmarks.harness import (
    DEFAULT_FIXTURE_ID,
    DEFAULT_MASTER_SEED,
    DEFAULT_SIMULATION_RUN_ID,
)


def load_benchmark_game(fixture_id: str = DEFAULT_FIXTURE_ID) -> GameVersion:
    return load_golden_game_version(fixture_id)


def benchmark_profile(
    *,
    spin_count: int,
    shard_count: int = 1,
    master_seed: bytes = DEFAULT_MASTER_SEED,
    simulation_run_id: str = DEFAULT_SIMULATION_RUN_ID,
) -> SimulationProfile:
    return SimulationProfile(
        spinCount=spin_count,
        shardCount=shard_count,
        masterSeed=master_seed,
        simulationRunId=simulation_run_id,
    )
