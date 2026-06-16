"""Exposure truncation analysis from simulation aggregates."""

from __future__ import annotations

from runtime_core.mathematical.models import ExposureAnalysisResult
from runtime_core.simulation.models import SimulationResult


def calculate_exposure_analysis(result: SimulationResult) -> ExposureAnalysisResult:
    """Analyze exposure cap impact on RTP."""
    total_bet = result.total_bet_minor_units
    total_spins = result.spin_count
    if total_bet <= 0:
        capped_rtp = 0.0
        uncapped_rtp = 0.0
    else:
        capped_rtp = result.total_win_minor_units / total_bet
        uncapped_rtp = result.uncapped_win_minor_units / total_bet

    truncation_rate = (
        result.exposure_truncation_count / total_spins if total_spins > 0 else 0.0
    )
    return ExposureAnalysisResult(
        truncation_rate=truncation_rate,
        total_truncated_minor_units=result.exposure_truncated_minor_units,
        capped_rtp=capped_rtp,
        uncapped_rtp=uncapped_rtp,
        rtp_difference=uncapped_rtp - capped_rtp,
    )
