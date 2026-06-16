"""Edge-case coverage for mathematical engine."""

from __future__ import annotations

import pytest

from runtime_core.mathematical.confidence import calculate_rtp_confidence_interval
from runtime_core.mathematical.distribution import calculate_win_distribution
from runtime_core.mathematical.golden import GoldenMathDiff, _compare_report
from runtime_core.mathematical.models import (
    ConfidenceIntervalResult,
    ExposureAnalysisResult,
    FeatureFrequencyResult,
    HitFrequencyResult,
    JackpotFrequencyResult,
    MathematicsReport,
    RTPResult,
    VolatilityResult,
    WinDistributionBucket,
    WinDistributionResult,
)
from runtime_core.mathematical.report import build_mathematics_report
from runtime_core.mathematical.volatility import calculate_volatility
from tests.mathematical.conftest import sample_simulation_result
from tests.mathematical.report_helpers import empty_rtp_decomposition


def test_distribution_high_multiplier_bucket() -> None:
    result = sample_simulation_result(spin_count=2, total_bet=2000, total_win=1_100_000)
    distribution = calculate_win_distribution(result, (600_000, 501_000))
    labels = {bucket.label: bucket.count for bucket in distribution.buckets}
    assert labels["500x+"] == 2


def test_distribution_length_mismatch() -> None:
    result = sample_simulation_result(spin_count=2, total_bet=2000)
    with pytest.raises(ValueError, match="spin_wins length"):
        calculate_win_distribution(result, (100,))


def test_volatility_length_mismatch() -> None:
    result = sample_simulation_result(spin_count=2, total_bet=2000)
    with pytest.raises(ValueError, match="spin_wins length"):
        calculate_volatility(result, (100,))


def test_confidence_zero_bet_per_spin() -> None:
    result = sample_simulation_result(spin_count=2, total_bet=0, total_win=0)
    ci = calculate_rtp_confidence_interval(result, (0, 0))
    assert ci.lower_bound == 0.0
    assert ci.upper_bound == 0.0


def test_report_spin_wins_length_mismatch() -> None:
    result = sample_simulation_result(spin_count=2, total_bet=2000)
    with pytest.raises(ValueError, match="spin_wins length"):
        build_mathematics_report(result, spin_wins_minor_units=(100,))


def test_golden_compare_missing_feature_and_jackpot() -> None:
    report = MathematicsReport(
        rtp=RTPResult(
            rtp=1.0,
            uncapped_rtp=1.0,
            total_bet_minor_units=1000,
            total_win_minor_units=1000,
            uncapped_win_minor_units=1000,
        ),
        hit_frequency=HitFrequencyResult(
            hit_frequency=1.0,
            winning_spin_count=1,
            losing_spin_count=0,
        ),
        feature_frequencies=(),
        jackpot_frequencies=(),
        volatility=VolatilityResult(
            mean_win_minor_units=1000.0,
            variance=0.0,
            standard_deviation=0.0,
            coefficient_of_variation=None,
        ),
        exposure=ExposureAnalysisResult(
            truncation_rate=0.0,
            total_truncated_minor_units=0,
            capped_rtp=1.0,
            uncapped_rtp=1.0,
            rtp_difference=0.0,
        ),
        confidence_interval=ConfidenceIntervalResult(
            lower_bound=1.0,
            upper_bound=1.0,
            confidence_level=0.95,
        ),
        win_distribution=WinDistributionResult(
            total_spins=1,
            bet_minor_units_per_spin=1000,
            buckets=(
                WinDistributionBucket(label="0x", count=0, percentage=0.0),
            ),
        ),
        rtp_decomposition=empty_rtp_decomposition(total_rtp=1.0),
        spin_count=1,
        engine_version="runtime-core@1.8.0",
    )
    metrics = {
        "rtp": 1.0,
        "uncappedRtp": 1.0,
        "hitFrequency": 1.0,
        "winningSpinCount": 1,
        "losingSpinCount": 0,
        "meanWinMinorUnits": 1000.0,
        "variance": 0.0,
        "standardDeviation": 0.0,
        "coefficientOfVariation": None,
        "truncationRate": 0.0,
        "totalTruncatedMinorUnits": 0,
        "cappedRtp": 1.0,
        "uncappedRtpExposure": 1.0,
        "rtpDifference": 0.0,
        "confidenceLowerBound": 1.0,
        "confidenceUpperBound": 1.0,
        "confidenceLevel": 0.95,
        "distributionBuckets": {"0x": 0},
        "featureFrequencies": {
            "MISSING": {"triggerCount": 1, "frequency": 1.0, "oneInX": 1.0},
        },
        "jackpotFrequencies": {
            "MAJOR": {"triggerCount": 1, "frequency": 1.0, "oneInX": 1.0},
        },
    }
    diffs = _compare_report(report, metrics)
    assert any(diff.field.startswith("featureFrequencies.MISSING") for diff in diffs)
    assert any(diff.field.startswith("jackpotFrequencies.MAJOR") for diff in diffs)


def test_golden_compare_none_coefficient() -> None:
    diffs: list[GoldenMathDiff] = []
    from runtime_core.mathematical.golden import _check_float

    _check_float(diffs, "coefficientOfVariation", 1.0, None)
    assert diffs[0].actual == "None"
