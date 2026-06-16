"""RTP decomposition by rtpCategory from simulation aggregates."""

from __future__ import annotations

from runtime_core.mathematical.models import RtpCategoryContribution, RtpDecompositionResult
from runtime_core.simulation.models import SimulationResult


def calculate_rtp_decomposition(
    result: SimulationResult,
) -> RtpDecompositionResult:
    """Break total RTP into per-category win contributions."""
    total_bet = result.total_bet_minor_units
    if total_bet <= 0:
        return RtpDecompositionResult(
            total_rtp=0.0,
            categories=(),
        )

    total_rtp = result.total_win_minor_units / total_bet
    categories: list[RtpCategoryContribution] = []
    for category in sorted(result.win_by_rtp_category_minor_units):
        win_minor = result.win_by_rtp_category_minor_units[category]
        share = win_minor / total_bet
        categories.append(
            RtpCategoryContribution(
                rtp_category=category,
                win_minor_units=win_minor,
                rtp_share=share,
            ),
        )

    return RtpDecompositionResult(
        total_rtp=total_rtp,
        categories=tuple(categories),
    )
