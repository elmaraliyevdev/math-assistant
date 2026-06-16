"""Simulation test helpers."""

from __future__ import annotations

from runtime_core.common.golden import load_golden_game_version
from runtime_core.domain.game_version import GameVersion
from runtime_core.golden.models import RuntimeOverrides
from runtime_core.golden.overrides import apply_runtime_overrides
from runtime_core.simulation.models import SimulationProfile


def simulation_profile(
    *,
    spin_count: int,
    master_seed: bytes = b"sim-test-seed",
    shard_count: int = 1,
    simulation_run_id: str = "sim-test-run",
    sample_events: int = 0,
    max_faults: int | None = None,
) -> SimulationProfile:
    return SimulationProfile(
        spinCount=spin_count,
        shardCount=shard_count,
        masterSeed=master_seed,
        simulationRunId=simulation_run_id,
        sampleEvents=sample_events,
        maxFaults=max_faults,
    )


def load_fixture_for_simulation(fixture_id: str) -> GameVersion:
    game = load_golden_game_version(fixture_id)
    if "hold-win" in fixture_id or "nested" in fixture_id:
        return apply_runtime_overrides(
            game,
            RuntimeOverrides(
                hold_and_win_entry_min_count=3,
                hold_and_win_trigger_symbol_count=3,
            ),
        )
    return game
