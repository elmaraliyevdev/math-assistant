"""Volatility metric tests."""

from __future__ import annotations

import pytest

from runtime_core.mathematical.volatility import calculate_volatility
from tests.mathematical.conftest import SAMPLE_SPIN_WINS, sample_simulation_result


def test_volatility_metrics() -> None:
    result = sample_simulation_result(spin_count=4)
    vol = calculate_volatility(result, SAMPLE_SPIN_WINS)
    assert vol.mean_win_minor_units == 1875.0
    assert vol.variance == pytest.approx(3_796_875.0)
    assert vol.standard_deviation == pytest.approx(1948.557158514987)
    assert vol.coefficient_of_variation == pytest.approx(1.0392304845413263)


def test_volatility_zero_spins() -> None:
    result = sample_simulation_result(spin_count=0, total_bet=0, total_win=0)
    vol = calculate_volatility(result, ())
    assert vol.mean_win_minor_units == 0.0
    assert vol.coefficient_of_variation is None


def test_volatility_all_zero_wins() -> None:
    result = sample_simulation_result(spin_count=3, total_bet=3000, total_win=0)
    vol = calculate_volatility(result, (0, 0, 0))
    assert vol.mean_win_minor_units == 0.0
    assert vol.coefficient_of_variation is None
