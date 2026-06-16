"""Assemble game-design insights from simulation output."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.mathematical.decomposition_chart import build_rtp_decomposition_chart
from runtime_core.mathematical.feature_validation import validate_feature_frequencies
from runtime_core.mathematical.models import MathematicsReport
from runtime_core.mathematical.recommendations import generate_recommendations
from runtime_core.mathematical.rtp_validation import validate_rtp_target
from runtime_core.simulation.models import SimulationResult


def enrich_mathematics_report(
    report: MathematicsReport,
    *,
    game: GameVersion,
    result: SimulationResult,
    feature_frequency_tolerance: float = 0.05,
) -> MathematicsReport:
    """Attach RTP validation, decomposition chart, and recommendations."""
    rtp_validation = validate_rtp_target(result, game, actual_rtp_ratio=report.rtp.rtp)
    chart = build_rtp_decomposition_chart(result, game)
    feature_validation = validate_feature_frequencies(
        result,
        game,
        tolerance=feature_frequency_tolerance,
    )
    recommendations = generate_recommendations(
        result,
        game,
        rtp_validation=rtp_validation,
    )
    return report.model_copy(
        update={
            "rtp_validation": rtp_validation,
            "rtp_decomposition_chart": chart,
            "feature_validation": feature_validation,
            "recommendations": recommendations,
        },
    )
