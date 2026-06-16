"""RTP calculation from simulation aggregates."""

from __future__ import annotations

from runtime_core.mathematical.models import RTPResult
from runtime_core.simulation.models import SimulationResult


def calculate_rtp(result: SimulationResult) -> RTPResult:
    """Compute capped and uncapped RTP ratios from *result* totals."""
    total_bet = result.total_bet_minor_units
    if total_bet <= 0:
        return RTPResult(
            rtp=0.0,
            uncapped_rtp=0.0,
            total_bet_minor_units=total_bet,
            total_win_minor_units=result.total_win_minor_units,
            uncapped_win_minor_units=result.uncapped_win_minor_units,
        )
    return RTPResult(
        rtp=result.total_win_minor_units / total_bet,
        uncapped_rtp=result.uncapped_win_minor_units / total_bet,
        total_bet_minor_units=total_bet,
        total_win_minor_units=result.total_win_minor_units,
        uncapped_win_minor_units=result.uncapped_win_minor_units,
    )
