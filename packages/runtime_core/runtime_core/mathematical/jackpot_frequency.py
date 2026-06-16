"""Jackpot hit frequency from simulation aggregates."""

from __future__ import annotations

from runtime_core.mathematical.models import JackpotFrequencyResult
from runtime_core.simulation.models import SimulationResult


def calculate_jackpot_frequencies(
    result: SimulationResult,
) -> tuple[JackpotFrequencyResult, ...]:
    """Derive jackpot tier rates from *result.jackpot_counts*."""
    total_spins = result.spin_count
    if total_spins <= 0:
        return ()

    frequencies: list[JackpotFrequencyResult] = []
    for tier in sorted(result.jackpot_counts):
        trigger_count = result.jackpot_counts[tier]
        frequency = trigger_count / total_spins
        one_in_x = (total_spins / trigger_count) if trigger_count > 0 else None
        frequencies.append(
            JackpotFrequencyResult(
                jackpot_tier=tier,
                trigger_count=trigger_count,
                frequency=frequency,
                one_in_x=one_in_x,
            ),
        )
    return tuple(frequencies)
