"""Hit frequency from per-spin win outcomes."""

from __future__ import annotations

from runtime_core.mathematical.models import HitFrequencyResult
from runtime_core.simulation.models import SimulationResult


def calculate_hit_frequency(
    result: SimulationResult,
    spin_wins_minor_units: tuple[int, ...],
) -> HitFrequencyResult:
    """Compute winningSpins / totalSpins from per-spin win amounts."""
    total_spins = result.spin_count
    if total_spins == 0:
        return HitFrequencyResult(
            hit_frequency=0.0,
            winning_spin_count=0,
            losing_spin_count=0,
        )
    if len(spin_wins_minor_units) != total_spins:
        msg = (
            f"spin_wins length {len(spin_wins_minor_units)} "
            f"!= spin_count {total_spins}"
        )
        raise ValueError(msg)

    winning = sum(1 for win in spin_wins_minor_units if win > 0)
    losing = total_spins - winning
    return HitFrequencyResult(
        hit_frequency=winning / total_spins,
        winning_spin_count=winning,
        losing_spin_count=losing,
    )
