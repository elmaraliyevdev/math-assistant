"""SimulationRunner and process-pool integration tests."""

from __future__ import annotations

from runtime_core.simulation.models import SimulationProfile
from runtime_core.simulation.runner import SimulationRunner, run_simulation
from runtime_core.simulation.sharding import assign_shards
from tests.simulation.conftest import load_fixture_for_simulation, simulation_profile


def test_simulation_runner_delegates_to_run_simulation() -> None:
    game = load_fixture_for_simulation("fixture-01-base-5x3")
    profile = simulation_profile(spin_count=5, shard_count=2)
    direct = run_simulation(game, profile)
    via_runner = SimulationRunner(max_workers=2).run(game, profile)
    assert direct.model_dump(exclude={"elapsed_time_ms"}) == via_runner.model_dump(
        exclude={"elapsed_time_ms"},
    )


def test_max_faults_stops_shard_early() -> None:
    game = load_fixture_for_simulation("fixture-01-base-5x3")
    unlimited = run_simulation(
        game,
        simulation_profile(spin_count=20, shard_count=1, max_faults=None),
    )
    limited = run_simulation(
        game,
        simulation_profile(spin_count=20, shard_count=1, max_faults=0),
    )
    assert limited.spin_count == 20
    assert limited.chain_fault_count <= unlimited.chain_fault_count


def test_master_seed_utf8_string_coercion() -> None:
    profile = SimulationProfile.model_validate(
        {
            "spinCount": 1,
            "shardCount": 1,
            "masterSeed": "plain-text-seed",
            "simulationRunId": "run",
        },
    )
    assert profile.master_seed == b"plain-text-seed"


def test_assign_shards_rejects_invalid_inputs() -> None:
    import pytest

    with pytest.raises(ValueError, match="total_spins"):
        assign_shards(-1, 1, master_seed=b"s", simulation_run_id="run")
    with pytest.raises(ValueError, match="shard_count"):
        assign_shards(10, 0, master_seed=b"s", simulation_run_id="run")


def test_assign_shards_derives_distinct_shard_seeds() -> None:
    from runtime_core.runtime.rng.service import derive_shard_seed

    assignments = assign_shards(
        4,
        2,
        master_seed=b"seed",
        simulation_run_id="run",
    )
    assert assignments[0].shard_seed == derive_shard_seed(b"seed", 0, "run")
    assert assignments[1].shard_seed == derive_shard_seed(b"seed", 1, "run")
    assert assignments[0].shard_seed != assignments[1].shard_seed
