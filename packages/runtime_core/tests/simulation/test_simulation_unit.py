"""Simulation Engine unit tests."""

from __future__ import annotations

import pytest

from runtime_core.simulation.aggregator import AccumulatorAggregator, PartialAccumulator
from runtime_core.simulation.models import SimulationProfile
from runtime_core.simulation.sharding import assign_shards
from runtime_core.simulation.runner import run_simulation
from tests.simulation.conftest import load_fixture_for_simulation, simulation_profile


def test_assign_shards_even_split() -> None:
    assignments = assign_shards(
        10,
        4,
        master_seed=b"seed",
        simulation_run_id="run",
    )
    assert sum(item.spin_count for item in assignments) == 10
    assert [item.spin_count for item in assignments] == [3, 3, 2, 2]
    assert assignments[0].spin_start == 0
    assert assignments[1].spin_start == 3


def test_assign_shards_zero_spins() -> None:
    assignments = assign_shards(
        0,
        3,
        master_seed=b"seed",
        simulation_run_id="run",
    )
    assert all(item.spin_count == 0 for item in assignments)


def test_partial_accumulator_merge_commutative() -> None:
    left = PartialAccumulator(
        spin_count=2,
        total_bet_minor_units=100,
        total_win_minor_units=10,
        feature_trigger_counts={"FREE_SPINS": 1},
        jackpot_counts={"MINI": 1},
    )
    right = PartialAccumulator(
        spin_count=3,
        total_bet_minor_units=150,
        total_win_minor_units=5,
        feature_trigger_counts={"HOLD_AND_WIN": 2},
        jackpot_counts={"MINI": 1, "MAJOR": 1},
    )
    merged_ab = left.merge(right)
    merged_ba = right.merge(left)
    assert merged_ab == merged_ba
    assert merged_ab.spin_count == 5
    assert merged_ab.feature_trigger_counts["FREE_SPINS"] == 1
    assert merged_ab.jackpot_counts["MAJOR"] == 1


def test_aggregator_empty() -> None:
    assert AccumulatorAggregator.aggregate(()).spin_count == 0


def test_simulation_profile_accepts_hex_seed() -> None:
    profile = SimulationProfile.model_validate(
        {
            "spinCount": 1,
            "shardCount": 1,
            "masterSeed": "deadbeef",
            "simulationRunId": "run",
        },
    )
    assert profile.master_seed == bytes.fromhex("deadbeef")


def test_run_simulation_zero_spins() -> None:
    game = load_fixture_for_simulation("fixture-01-base-5x3")
    result = run_simulation(game, simulation_profile(spin_count=0))
    assert result.spin_count == 0
    assert result.total_bet_minor_units == 0


def test_run_simulation_single_chain() -> None:
    game = load_fixture_for_simulation("fixture-01-base-5x3")
    result = run_simulation(
        game,
        simulation_profile(spin_count=1, master_seed=b"single-chain"),
    )
    assert result.spin_count == 1
    assert result.total_bet_minor_units > 0
    assert result.elapsed_time_ms >= 0


def test_sample_events_count() -> None:
    game = load_fixture_for_simulation("fixture-01-base-5x3")
    result = run_simulation(
        game,
        simulation_profile(spin_count=5, sample_events=2),
    )
    assert result.event_sample_count == 2
