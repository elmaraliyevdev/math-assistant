"""Volatility metrics using NumPy."""

from __future__ import annotations

import numpy as np

from runtime_core.mathematical.models import VolatilityResult
from runtime_core.simulation.models import SimulationResult


def calculate_volatility(
    result: SimulationResult,
    spin_wins_minor_units: tuple[int, ...],
) -> VolatilityResult:
    """
    Compute per-spin win dispersion.

    μ = totalWin / spinCount
    σ² = (winSumSquares / spinCount) - μ²  (population variance)
    """
    total_spins = result.spin_count
    if total_spins == 0:
        return VolatilityResult(
            mean_win_minor_units=0.0,
            variance=0.0,
            standard_deviation=0.0,
            coefficient_of_variation=None,
        )
    if len(spin_wins_minor_units) != total_spins:
        msg = (
            f"spin_wins length {len(spin_wins_minor_units)} "
            f"!= spin_count {total_spins}"
        )
        raise ValueError(msg)

    wins = np.asarray(spin_wins_minor_units, dtype=np.float64)
    mean_win = float(np.mean(wins))
    variance = float(np.var(wins))
    std_dev = float(np.std(wins))
    cv = (std_dev / mean_win) if mean_win > 0 else None
    return VolatilityResult(
        mean_win_minor_units=mean_win,
        variance=variance,
        standard_deviation=std_dev,
        coefficient_of_variation=cv,
    )
