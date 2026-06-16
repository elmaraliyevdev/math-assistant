"""RTP confidence interval tests."""

from __future__ import annotations

import pytest

from runtime_core.mathematical.confidence import calculate_rtp_confidence_interval
from tests.mathematical.conftest import SAMPLE_SPIN_WINS, sample_simulation_result


def test_rtp_confidence_interval_95() -> None:
    result = sample_simulation_result(spin_count=4, total_bet=4000)
    ci = calculate_rtp_confidence_interval(result, SAMPLE_SPIN_WINS)
    assert ci.confidence_level == 0.95
    assert ci.lower_bound == pytest.approx(-0.33, rel=1e-4)
    assert ci.upper_bound == pytest.approx(4.08, rel=1e-4)


def test_rtp_confidence_interval_zero_spins() -> None:
    result = sample_simulation_result(spin_count=0, total_bet=0, total_win=0)
    ci = calculate_rtp_confidence_interval(result, ())
    assert ci.lower_bound == 0.0
    assert ci.upper_bound == 0.0


def test_rtp_confidence_interval_single_spin() -> None:
    result = sample_simulation_result(spin_count=1, total_bet=1000, total_win=500)
    ci = calculate_rtp_confidence_interval(result, (500,))
    assert ci.lower_bound == 0.5
    assert ci.upper_bound == 0.5


def test_unsupported_confidence_level() -> None:
    result = sample_simulation_result(spin_count=4, total_bet=4000)
    with pytest.raises(ValueError, match="unsupported confidence level"):
        calculate_rtp_confidence_interval(
            result,
            SAMPLE_SPIN_WINS,
            confidence_level=0.99,
        )
