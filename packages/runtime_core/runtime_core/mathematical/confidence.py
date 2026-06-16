"""Confidence intervals for RTP."""

from __future__ import annotations

import numpy as np

from runtime_core.mathematical.models import ConfidenceIntervalResult
from runtime_core.simulation.models import SimulationResult

_Z_SCORE_95 = 1.96


def calculate_rtp_confidence_interval(
    result: SimulationResult,
    spin_wins_minor_units: tuple[int, ...],
    *,
    confidence_level: float = 0.95,
) -> ConfidenceIntervalResult:
    """
    Normal-approximation CI for per-spin return RTP.

    return_i = win_i / bet_i
    RTP = mean(return_i)
    CI = RTP ± z * (std(return_i) / sqrt(n))
    """
    total_spins = result.spin_count
    if total_spins == 0:
        return ConfidenceIntervalResult(
            lower_bound=0.0,
            upper_bound=0.0,
            confidence_level=confidence_level,
        )
    if len(spin_wins_minor_units) != total_spins:
        msg = (
            f"spin_wins length {len(spin_wins_minor_units)} "
            f"!= spin_count {total_spins}"
        )
        raise ValueError(msg)

    bet_per_spin = result.total_bet_minor_units / total_spins
    if bet_per_spin <= 0:
        rtp = 0.0
        return ConfidenceIntervalResult(
            lower_bound=rtp,
            upper_bound=rtp,
            confidence_level=confidence_level,
        )

    returns = np.asarray(spin_wins_minor_units, dtype=np.float64) / bet_per_spin
    rtp = float(np.mean(returns))
    if total_spins == 1:
        return ConfidenceIntervalResult(
            lower_bound=rtp,
            upper_bound=rtp,
            confidence_level=confidence_level,
        )

    std = float(np.std(returns, ddof=1))
    margin = _z_score_for_level(confidence_level) * (std / np.sqrt(total_spins))
    return ConfidenceIntervalResult(
        lower_bound=rtp - margin,
        upper_bound=rtp + margin,
        confidence_level=confidence_level,
    )


def _z_score_for_level(confidence_level: float) -> float:
    if confidence_level == 0.95:
        return _Z_SCORE_95
    msg = f"unsupported confidence level {confidence_level}"
    raise ValueError(msg)
