"""RTP target validation against canonical metadata."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.mathematical.models import RtpValidationResult
from runtime_core.simulation.models import SimulationResult

DEFAULT_RTP_TOLERANCE_PERCENT = 0.1


def validate_rtp_target(
    result: SimulationResult,
    game: GameVersion,
    *,
    actual_rtp_ratio: float | None = None,
) -> RtpValidationResult | None:
    """Compare simulation RTP to ``metadata.rtpTarget`` when configured."""
    metadata = game.metadata
    if metadata is None or metadata.rtp_target is None:
        return None

    target = metadata.rtp_target
    tolerance_percent = (
        target.tolerance if target.tolerance is not None else DEFAULT_RTP_TOLERANCE_PERCENT
    )
    target_percent = target.percent
    actual_ratio = actual_rtp_ratio
    if actual_ratio is None:
        if result.total_bet_minor_units <= 0:
            actual_ratio = 0.0
        else:
            actual_ratio = result.total_win_minor_units / result.total_bet_minor_units

    actual_percent = actual_ratio * 100.0
    difference_percent = actual_percent - target_percent
    within = abs(difference_percent) <= tolerance_percent

    return RtpValidationResult(
        target_rtp=target_percent,
        actual_rtp=round(actual_percent, 4),
        difference=round(difference_percent, 4),
        tolerance=tolerance_percent,
        within_tolerance=within,
    )
