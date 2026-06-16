"""Golden mathematical validation loader and runner."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

from runtime_core.common.paths import find_repo_root
from runtime_core.mathematical.report import build_mathematics_report
from runtime_core.simulation.models import SimulationResult


class GoldenMathInput(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    simulation_result: SimulationResult = Field(alias="simulationResult")
    spin_wins_minor_units: tuple[int, ...] = Field(alias="spinWinsMinorUnits")


class GoldenMathExpected(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    version: str
    locked: bool
    metrics: dict[str, Any]


class GoldenMathDiff(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    field: str
    expected: str
    actual: str


class GoldenMathComparisonResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    fixture_id: str = Field(alias="fixtureId")
    passed: bool
    diffs: tuple[GoldenMathDiff, ...]


def list_golden_math_fixtures(*, repo_root: Path | None = None) -> list[str]:
    root = repo_root or find_repo_root()
    manifest = root / "tests/golden/mathematical/manifest.yaml"
    data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    return [item["id"] for item in data["fixtures"]]


def load_golden_math_input(
    fixture_id: str,
    *,
    repo_root: Path | None = None,
) -> GoldenMathInput:
    root = repo_root or find_repo_root()
    path = root / "tests/golden/mathematical" / fixture_id / "input.yaml"
    return GoldenMathInput.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def load_golden_math_expected(
    fixture_id: str,
    *,
    repo_root: Path | None = None,
) -> GoldenMathExpected:
    root = repo_root or find_repo_root()
    path = root / "tests/golden/mathematical" / fixture_id / "expected.yaml"
    return GoldenMathExpected.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def validate_golden_math_fixture(
    fixture_id: str,
    *,
    repo_root: Path | None = None,
) -> GoldenMathComparisonResult:
    golden_input = load_golden_math_input(fixture_id, repo_root=repo_root)
    expected = load_golden_math_expected(fixture_id, repo_root=repo_root)
    report = build_mathematics_report(
        golden_input.simulation_result,
        spin_wins_minor_units=golden_input.spin_wins_minor_units,
    )
    diffs = _compare_report(report, expected.metrics)
    return GoldenMathComparisonResult(
        fixture_id=fixture_id,
        passed=not diffs,
        diffs=tuple(diffs),
    )


def _compare_report(report, metrics: dict[str, Any]) -> list[GoldenMathDiff]:
    diffs: list[GoldenMathDiff] = []
    _check_float(diffs, "rtp", metrics["rtp"], report.rtp.rtp)
    _check_float(diffs, "uncappedRtp", metrics["uncappedRtp"], report.rtp.uncapped_rtp)
    _check_float(
        diffs,
        "hitFrequency",
        metrics["hitFrequency"],
        report.hit_frequency.hit_frequency,
    )
    _check_int(
        diffs,
        "winningSpinCount",
        metrics["winningSpinCount"],
        report.hit_frequency.winning_spin_count,
    )
    _check_int(
        diffs,
        "losingSpinCount",
        metrics["losingSpinCount"],
        report.hit_frequency.losing_spin_count,
    )
    _check_float(
        diffs,
        "meanWinMinorUnits",
        metrics["meanWinMinorUnits"],
        report.volatility.mean_win_minor_units,
    )
    _check_float(diffs, "variance", metrics["variance"], report.volatility.variance)
    _check_float(
        diffs,
        "standardDeviation",
        metrics["standardDeviation"],
        report.volatility.standard_deviation,
    )
    _check_float(
        diffs,
        "coefficientOfVariation",
        metrics["coefficientOfVariation"],
        report.volatility.coefficient_of_variation,
    )
    _check_float(
        diffs,
        "truncationRate",
        metrics["truncationRate"],
        report.exposure.truncation_rate,
    )
    _check_int(
        diffs,
        "totalTruncatedMinorUnits",
        metrics["totalTruncatedMinorUnits"],
        report.exposure.total_truncated_minor_units,
    )
    _check_float(diffs, "cappedRtp", metrics["cappedRtp"], report.exposure.capped_rtp)
    _check_float(
        diffs,
        "uncappedRtpExposure",
        metrics["uncappedRtpExposure"],
        report.exposure.uncapped_rtp,
    )
    _check_float(
        diffs,
        "rtpDifference",
        metrics["rtpDifference"],
        report.exposure.rtp_difference,
    )
    _check_float(
        diffs,
        "confidenceLowerBound",
        metrics["confidenceLowerBound"],
        report.confidence_interval.lower_bound,
    )
    _check_float(
        diffs,
        "confidenceUpperBound",
        metrics["confidenceUpperBound"],
        report.confidence_interval.upper_bound,
    )
    _check_float(
        diffs,
        "confidenceLevel",
        metrics["confidenceLevel"],
        report.confidence_interval.confidence_level,
    )

    expected_buckets = metrics["distributionBuckets"]
    actual_buckets = {bucket.label: bucket.count for bucket in report.win_distribution.buckets}
    for label, expected_count in expected_buckets.items():
        actual_count = actual_buckets.get(label)
        if actual_count != expected_count:
            diffs.append(
                GoldenMathDiff(
                    field=f"distributionBuckets.{label}",
                    expected=str(expected_count),
                    actual=str(actual_count),
                ),
            )

    for feature_name, feature_metrics in metrics["featureFrequencies"].items():
        actual = next(
            (item for item in report.feature_frequencies if item.feature_name == feature_name),
            None,
        )
        if actual is None:
            diffs.append(
                GoldenMathDiff(
                    field=f"featureFrequencies.{feature_name}",
                    expected=str(feature_metrics),
                    actual="missing",
                ),
            )
            continue
        _check_int(
            diffs,
            f"featureFrequencies.{feature_name}.triggerCount",
            feature_metrics["triggerCount"],
            actual.trigger_count,
        )
        _check_float(
            diffs,
            f"featureFrequencies.{feature_name}.frequency",
            feature_metrics["frequency"],
            actual.frequency,
        )
        _check_float(
            diffs,
            f"featureFrequencies.{feature_name}.oneInX",
            feature_metrics["oneInX"],
            actual.one_in_x,
        )

    for tier, jackpot_metrics in metrics["jackpotFrequencies"].items():
        actual = next(
            (item for item in report.jackpot_frequencies if item.jackpot_tier == tier),
            None,
        )
        if actual is None:
            diffs.append(
                GoldenMathDiff(
                    field=f"jackpotFrequencies.{tier}",
                    expected=str(jackpot_metrics),
                    actual="missing",
                ),
            )
            continue
        _check_int(
            diffs,
            f"jackpotFrequencies.{tier}.triggerCount",
            jackpot_metrics["triggerCount"],
            actual.trigger_count,
        )
        _check_float(
            diffs,
            f"jackpotFrequencies.{tier}.frequency",
            jackpot_metrics["frequency"],
            actual.frequency,
        )
        _check_float(
            diffs,
            f"jackpotFrequencies.{tier}.oneInX",
            jackpot_metrics["oneInX"],
            actual.one_in_x,
        )

    return diffs


def _check_float(
    diffs: list[GoldenMathDiff],
    field: str,
    expected: float,
    actual: float | None,
) -> None:
    if actual is None:
        diffs.append(GoldenMathDiff(field=field, expected=str(expected), actual="None"))
        return
    if abs(actual - expected) > 1e-6:
        diffs.append(
            GoldenMathDiff(field=field, expected=str(expected), actual=str(actual)),
        )


def _check_int(
    diffs: list[GoldenMathDiff],
    field: str,
    expected: int,
    actual: int,
) -> None:
    if actual != expected:
        diffs.append(
            GoldenMathDiff(field=field, expected=str(expected), actual=str(actual)),
        )
