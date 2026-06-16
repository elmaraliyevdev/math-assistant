"""Simulation determinism and sharding equivalence tests."""

from __future__ import annotations

import pytest

from runtime_core.simulation.runner import run_simulation
from tests.simulation.conftest import load_fixture_for_simulation, simulation_profile


@pytest.mark.parametrize("shard_count", [1, 2, 4])
def test_shard_equivalence_fixture_01(shard_count: int) -> None:
    game = load_fixture_for_simulation("fixture-01-base-5x3")
    profile = simulation_profile(
        spin_count=40,
        shard_count=shard_count,
        master_seed=b"shard-equiv-01",
        simulation_run_id="shard-equiv-run",
    )
    result = run_simulation(game, profile)
    assert result.spin_count == 40
    assert result.total_bet_minor_units == 40 * 2000

    baseline = run_simulation(
        game,
        simulation_profile(
            spin_count=40,
            shard_count=1,
            master_seed=b"shard-equiv-01",
            simulation_run_id="shard-equiv-run",
        ),
    )
    assert result.total_win_minor_units == baseline.total_win_minor_units
    assert result.uncapped_win_minor_units == baseline.uncapped_win_minor_units
    assert result.chain_fault_count == baseline.chain_fault_count
    assert result.feature_trigger_counts == baseline.feature_trigger_counts
    assert result.jackpot_counts == baseline.jackpot_counts
    assert result.event_sample_count == baseline.event_sample_count


def test_same_seed_produces_identical_results() -> None:
    game = load_fixture_for_simulation("fixture-01-base-5x3")
    kwargs = dict(
        spin_count=25,
        shard_count=2,
        master_seed=b"determinism-seed",
        simulation_run_id="determinism-run",
    )
    first = run_simulation(game, simulation_profile(**kwargs))
    second = run_simulation(game, simulation_profile(**kwargs))
    assert first.model_dump(exclude={"elapsed_time_ms"}) == second.model_dump(
        exclude={"elapsed_time_ms"},
    )


def test_different_seeds_produce_different_results() -> None:
    game = load_fixture_for_simulation("fixture-02-base-free-spins")
    base_kwargs = dict(spin_count=30, shard_count=1, simulation_run_id="seed-compare")
    first = run_simulation(
        game,
        simulation_profile(master_seed=b"seed-alpha", **base_kwargs),
    )
    second = run_simulation(
        game,
        simulation_profile(master_seed=b"seed-beta", **base_kwargs),
    )
    assert (
        first.feature_trigger_counts != second.feature_trigger_counts
        or first.total_win_minor_units != second.total_win_minor_units
    )


@pytest.mark.parametrize(
    "fixture_id",
    [
        "fixture-01-base-5x3",
        "fixture-02-base-free-spins",
        "fixture-03-base-hold-win",
        "fixture-04-nested-fs-hold-win",
    ],
)
def test_golden_fixtures_execute_successfully(fixture_id: str) -> None:
    game = load_fixture_for_simulation(fixture_id)
    result = run_simulation(
        game,
        simulation_profile(
            spin_count=3,
            shard_count=1,
            master_seed=f"golden-{fixture_id}".encode(),
            simulation_run_id="golden-sim",
        ),
    )
    assert result.spin_count == 3
    assert result.total_bet_minor_units == 3 * 2000
