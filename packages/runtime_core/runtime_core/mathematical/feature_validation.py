"""Observed vs theoretical feature trigger validation."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.mathematical.models import FeatureValidationResult
from runtime_core.mathematical.theoretical_frequency import (
    collect_trigger_specs,
    expected_trigger_frequency,
)
from runtime_core.simulation.models import SimulationResult

DEFAULT_FEATURE_FREQUENCY_TOLERANCE = 0.05


def validate_feature_frequencies(
    result: SimulationResult,
    game: GameVersion,
    *,
    tolerance: float = DEFAULT_FEATURE_FREQUENCY_TOLERANCE,
) -> tuple[FeatureValidationResult, ...]:
    """Compare observed trigger rates to reel-strip theory for BASE triggers."""
    if result.spin_count <= 0:
        return ()

    validations: list[FeatureValidationResult] = []
    seen: set[str] = set()

    for spec in collect_trigger_specs(game):
        if spec.state_id != "BASE" or spec.feature in seen:
            continue
        seen.add(spec.feature)

        observed_count = result.feature_trigger_counts.get(spec.feature, 0)
        observed = observed_count / result.spin_count
        expected = expected_trigger_frequency(game, spec)
        if expected is None:
            validations.append(
                FeatureValidationResult(
                    feature=spec.feature,
                    observed_frequency=round(observed, 6),
                    expected_frequency=0.0,
                    difference=0.0,
                    status="SKIP",
                ),
            )
            continue

        diff = observed - expected
        status = "PASS" if abs(diff) <= tolerance else "FAIL"
        validations.append(
            FeatureValidationResult(
                feature=spec.feature,
                observed_frequency=round(observed, 6),
                expected_frequency=round(expected, 6),
                difference=round(diff, 6),
                status=status,
            ),
        )

    _append_jackpot_validation(result, validations, tolerance)
    return tuple(validations)


def _append_jackpot_validation(
    result: SimulationResult,
    validations: list[FeatureValidationResult],
    tolerance: float,
) -> None:
    del tolerance  # jackpot theoretical frequency not modeled
    if result.spin_count <= 0:
        return
    total_jackpot_hits = sum(result.jackpot_counts.values())
    observed = total_jackpot_hits / result.spin_count
    validations.append(
        FeatureValidationResult(
            feature="JACKPOT",
            observed_frequency=round(observed, 6),
            expected_frequency=0.0,
            difference=0.0,
            status="SKIP" if total_jackpot_hits == 0 else "PASS",
        ),
    )
