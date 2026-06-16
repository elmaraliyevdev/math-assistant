"""Golden simulation tests for fixture-04-nested-fs-hold-win."""

from __future__ import annotations

from runtime_core.mathematical.feature_frequency import calculate_feature_frequencies
from runtime_core.mathematical.rtp_decomposition import calculate_rtp_decomposition
from runtime_core.simulation.runner import run_simulation
from tests.simulation.conftest import load_fixture_for_simulation, simulation_profile


def test_fixture_04_records_feature_triggers_and_rtp_decomposition() -> None:
    game = load_fixture_for_simulation("fixture-04-nested-fs-hold-win")
    result = run_simulation(
        game,
        simulation_profile(
            spin_count=10_000,
            master_seed=b"fixture-04-golden-sim",
            simulation_run_id="fixture-04-golden-sim",
        ),
    )

    assert result.spin_count == 10_000
    assert result.feature_trigger_counts.get("FREE_SPINS", 0) > 0
    assert result.feature_trigger_counts.get("HOLD_AND_WIN", 0) > 0
    assert result.nested_feature_entries > 0

    feature_frequencies = calculate_feature_frequencies(result)
    assert feature_frequencies
    feature_names = {item.feature_name for item in feature_frequencies}
    assert "FREE_SPINS" in feature_names
    assert "HOLD_AND_WIN" in feature_names

    decomposition = calculate_rtp_decomposition(result)
    assert decomposition.total_rtp > 0
    categories = {item.rtp_category for item in decomposition.categories}
    assert "BASE" in categories
    assert "FREE_SPINS" in categories
    assert "HOLD_AND_WIN" in categories

    category_rtp_sum = sum(item.rtp_share for item in decomposition.categories)
    assert abs(category_rtp_sum - decomposition.total_rtp) < 1e-9

    fs_frequency = next(
        item for item in feature_frequencies if item.feature_name == "FREE_SPINS"
    )
    assert fs_frequency.trigger_count > 1000
