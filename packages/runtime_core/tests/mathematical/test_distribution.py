"""Win distribution bucket tests."""

from __future__ import annotations

import pytest

from runtime_core.mathematical.distribution import calculate_win_distribution
from tests.mathematical.conftest import SAMPLE_SPIN_WINS, sample_simulation_result


def test_win_distribution_default_buckets() -> None:
    result = sample_simulation_result(spin_count=4, total_bet=4000)
    distribution = calculate_win_distribution(result, SAMPLE_SPIN_WINS)
    assert distribution.bet_minor_units_per_spin == 1000
    labels = {bucket.label: bucket for bucket in distribution.buckets}
    assert labels["0x"].count == 1
    assert labels["0-1x"].count == 1
    assert labels["1-5x"].count == 2
    assert labels["5-10x"].count == 0
    assert sum(bucket.count for bucket in distribution.buckets) == 4
    assert sum(bucket.percentage for bucket in distribution.buckets) == pytest.approx(1.0)


def test_win_distribution_zero_spins() -> None:
    result = sample_simulation_result(spin_count=0, total_bet=0, total_win=0)
    distribution = calculate_win_distribution(result, ())
    assert distribution.total_spins == 0
    assert len(distribution.buckets) == 8


def test_win_distribution_custom_labels_rejected() -> None:
    result = sample_simulation_result(spin_count=4)
    with pytest.raises(ValueError, match="custom bucket"):
        calculate_win_distribution(result, SAMPLE_SPIN_WINS, bucket_labels=("a", "b"))
