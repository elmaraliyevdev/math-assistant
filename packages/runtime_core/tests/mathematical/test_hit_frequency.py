"""Hit frequency tests."""

from __future__ import annotations

import pytest

from runtime_core.mathematical.hit_frequency import calculate_hit_frequency
from tests.mathematical.conftest import SAMPLE_SPIN_WINS, sample_simulation_result


def test_hit_frequency() -> None:
    result = sample_simulation_result(spin_count=4)
    hit = calculate_hit_frequency(result, SAMPLE_SPIN_WINS)
    assert hit.winning_spin_count == 3
    assert hit.losing_spin_count == 1
    assert hit.hit_frequency == 0.75


def test_hit_frequency_zero_spins() -> None:
    result = sample_simulation_result(spin_count=0, total_bet=0, total_win=0)
    hit = calculate_hit_frequency(result, ())
    assert hit.hit_frequency == 0.0


def test_hit_frequency_length_mismatch() -> None:
    result = sample_simulation_result(spin_count=4)
    with pytest.raises(ValueError, match="spin_wins length"):
        calculate_hit_frequency(result, (0, 500))
