"""Exposure analysis tests."""

from __future__ import annotations

import pytest

from runtime_core.mathematical.exposure import calculate_exposure_analysis
from tests.mathematical.conftest import sample_simulation_result


def test_exposure_analysis() -> None:
    result = sample_simulation_result(
        total_bet=10_000,
        total_win=9_000,
        uncapped_win=10_000,
        exposure_truncations=2,
        exposure_truncated=1_000,
    )
    exposure = calculate_exposure_analysis(result)
    assert exposure.truncation_rate == 0.5
    assert exposure.total_truncated_minor_units == 1_000
    assert exposure.capped_rtp == 0.9
    assert exposure.uncapped_rtp == 1.0
    assert exposure.rtp_difference == pytest.approx(0.1)


def test_exposure_zero_bet() -> None:
    result = sample_simulation_result(total_bet=0, total_win=0, uncapped_win=0)
    exposure = calculate_exposure_analysis(result)
    assert exposure.capped_rtp == 0.0
    assert exposure.uncapped_rtp == 0.0
