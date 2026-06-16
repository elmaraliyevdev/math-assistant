"""Compare observed runtime outcomes against golden expected baselines."""

from __future__ import annotations

from runtime_core.golden.models import (
    ExpectedBaseline,
    GoldenComparisonResult,
    GoldenDiff,
    GoldenRunOutcome,
)


def compare_outcome(
    fixture_id: str,
    expected: ExpectedBaseline,
    actual: GoldenRunOutcome,
    *,
    engine_version: str,
) -> GoldenComparisonResult:
    """Return comparison result with field-level diffs."""
    if not expected.locked:
        return GoldenComparisonResult(fixture_id=fixture_id, passed=True, diffs=())

    diffs: list[GoldenDiff] = []

    if expected.determinism.require_exact_engine_match:
        _append_diff(
            diffs,
            "engineVersion",
            expected.engine_version,
            engine_version,
        )

    outcome = expected.runtime_outcome
    _append_diff(diffs, "eventLogHash", outcome.event_log_hash, actual.event_log_hash)
    _append_diff(
        diffs,
        "totalWinMinorUnits",
        outcome.total_win_minor_units,
        actual.total_win_minor_units,
    )
    _append_diff(
        diffs,
        "totalBetMinorUnits",
        outcome.total_bet_minor_units,
        actual.total_bet_minor_units,
    )
    _append_diff(diffs, "stepCount", outcome.step_count, actual.step_count)
    _append_diff(
        diffs,
        "framePushCount",
        outcome.frame_push_count,
        actual.frame_push_count,
    )
    _append_diff(
        diffs,
        "exposure.capApplied",
        outcome.exposure.cap_applied,
        actual.exposure_cap_applied,
    )
    _append_diff(
        diffs,
        "exposure.truncatedMinorUnits",
        outcome.exposure.truncated_minor_units,
        actual.total_truncated_minor_units,
    )
    _append_diff(
        diffs,
        "exposure.uncappedWinMinorUnits",
        outcome.exposure.uncapped_win_minor_units,
        actual.total_uncapped_win_minor_units,
    )
    _append_diff(
        diffs,
        "exposure.truncationCount",
        outcome.exposure.truncation_count,
        actual.exposure_truncation_count,
    )
    _append_diff(
        diffs,
        "chainFaultCount",
        outcome.accumulator_delta.chain_fault_count,
        actual.chain_fault_count,
    )
    _append_diff(
        diffs,
        "accumulatorDelta.cappedWinMinorUnits",
        outcome.accumulator_delta.capped_win_minor_units,
        actual.capped_win_minor_units,
    )
    _append_diff(
        diffs,
        "accumulatorDelta.uncappedWinMinorUnits",
        outcome.accumulator_delta.uncapped_win_minor_units,
        actual.uncapped_win_minor_units,
    )
    _append_diff(
        diffs,
        "accumulatorDelta.exposureTruncationCount",
        outcome.accumulator_delta.exposure_truncation_count,
        actual.exposure_truncation_count,
    )
    _append_diff(
        diffs,
        "accumulatorDelta.exposureTruncatedMinorUnits",
        outcome.accumulator_delta.exposure_truncated_minor_units,
        actual.exposure_truncated_minor_units,
    )
    _append_diff(diffs, "fault", outcome.fault, actual.fault)
    _append_diff(diffs, "limitHit", outcome.limit_hit, actual.limit_hit)

    return GoldenComparisonResult(
        fixture_id=fixture_id,
        passed=not diffs,
        diffs=tuple(diffs),
    )


def format_diff_report(result: GoldenComparisonResult) -> str:
    """Render a human-readable diff report."""
    lines = [f"fixture: {result.fixture_id}", f"passed: {result.passed}"]
    if not result.diffs:
        return "\n".join(lines)
    lines.append("diffs:")
    for diff in result.diffs:
        lines.append(f"  - {diff.field}: expected={diff.expected!r} actual={diff.actual!r}")
    return "\n".join(lines)


def _append_diff(
    diffs: list[GoldenDiff],
    field: str,
    expected: object,
    actual: object,
) -> None:
    if expected != actual:
        diffs.append(
            GoldenDiff(
                field=field,
                expected=str(expected),
                actual=str(actual),
            ),
        )
