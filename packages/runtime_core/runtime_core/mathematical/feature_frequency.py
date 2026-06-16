"""Feature trigger frequency from simulation aggregates."""

from __future__ import annotations

from runtime_core.mathematical.models import FeatureFrequencyResult
from runtime_core.simulation.models import SimulationResult


def calculate_feature_frequencies(
    result: SimulationResult,
) -> tuple[FeatureFrequencyResult, ...]:
    """Derive feature trigger rates from *result.feature_trigger_counts*."""
    total_spins = result.spin_count
    if total_spins <= 0:
        return ()

    frequencies: list[FeatureFrequencyResult] = []
    for feature_name in sorted(result.feature_trigger_counts):
        trigger_count = result.feature_trigger_counts[feature_name]
        frequency = trigger_count / total_spins
        one_in_x = (total_spins / trigger_count) if trigger_count > 0 else None
        frequencies.append(
            FeatureFrequencyResult(
                feature_name=feature_name,
                trigger_count=trigger_count,
                frequency=frequency,
                one_in_x=one_in_x,
            ),
        )
    return tuple(frequencies)
