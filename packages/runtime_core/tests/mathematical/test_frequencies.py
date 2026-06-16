"""Feature and jackpot frequency tests."""

from __future__ import annotations

from runtime_core.mathematical.feature_frequency import calculate_feature_frequencies
from runtime_core.mathematical.jackpot_frequency import calculate_jackpot_frequencies
from tests.mathematical.conftest import sample_simulation_result


def test_feature_frequencies() -> None:
    result = sample_simulation_result(
        spin_count=100,
        feature_triggers={"FREE_SPINS": 5, "HOLD_AND_WIN": 2},
    )
    frequencies = calculate_feature_frequencies(result)
    assert len(frequencies) == 2
    fs = next(item for item in frequencies if item.feature_name == "FREE_SPINS")
    assert fs.trigger_count == 5
    assert fs.frequency == 0.05
    assert fs.one_in_x == 20.0


def test_jackpot_frequencies() -> None:
    result = sample_simulation_result(
        spin_count=1_000_000,
        jackpot_counts={"MINI": 10, "MAJOR": 1},
    )
    frequencies = calculate_jackpot_frequencies(result)
    mini = next(item for item in frequencies if item.jackpot_tier == "MINI")
    assert mini.frequency == 10 / 1_000_000
    assert mini.one_in_x == 100_000.0


def test_feature_frequencies_zero_spins() -> None:
    result = sample_simulation_result(spin_count=0, total_bet=0, total_win=0)
    assert calculate_feature_frequencies(result) == ()
    assert calculate_jackpot_frequencies(result) == ()
