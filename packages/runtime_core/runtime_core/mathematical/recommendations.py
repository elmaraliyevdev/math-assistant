"""Advisory recommendations from simulation mathematics."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.mathematical.decomposition_chart import build_rtp_decomposition_chart
from runtime_core.mathematical.models import RecommendationResult, RtpValidationResult
from runtime_core.simulation.models import SimulationResult


def generate_recommendations(
    result: SimulationResult,
    game: GameVersion,
    *,
    rtp_validation: RtpValidationResult | None = None,
) -> tuple[RecommendationResult, ...]:
    """Produce human-readable tuning suggestions (advisory only)."""
    recommendations: list[RecommendationResult] = []
    chart = build_rtp_decomposition_chart(result, game)

    actual_percent = chart.total_rtp
    target_percent = None
    if rtp_validation is not None:
        target_percent = rtp_validation.target_rtp
        actual_percent = rtp_validation.actual_rtp

    if target_percent is not None:
        gap = actual_percent - target_percent
        if gap < -5.0:
            recommendations.append(
                RecommendationResult(
                    severity="warning",
                    title="RTP Below Target",
                    description=(
                        "Increase paytable values or feature awards to close the "
                        f"{abs(gap):.1f} percentage-point gap to the {target_percent:.1f}% target."
                    ),
                ),
            )
        elif gap > 5.0:
            recommendations.append(
                RecommendationResult(
                    severity="warning",
                    title="RTP Above Target",
                    description=(
                        "Reduce paytable multipliers, feature awards, or jackpot tiers "
                        f"to lower RTP by {gap:.1f} percentage points."
                    ),
                ),
            )

    if chart.free_spins > 70.0:
        recommendations.append(
            RecommendationResult(
                severity="warning",
                title="High Free Spins RTP Share",
                description=(
                    f"Free Spins contributes {chart.free_spins:.1f}% of total RTP. "
                    "Reduce feature dependency by increasing base game RTP or lowering "
                    "free-spin award frequency."
                ),
            ),
        )

    if chart.base < 10.0:
        recommendations.append(
            RecommendationResult(
                severity="warning",
                title="Low Base RTP",
                description=(
                    f"Base RTP contributes only {chart.base:.1f}%. "
                    "Consider adding lower-tier symbol payouts or raising line-pay multipliers."
                ),
            ),
        )

    haw_triggers = result.feature_trigger_counts.get("HOLD_AND_WIN", 0)
    if chart.hold_and_win + chart.jackpot < 0.01 and haw_triggers == 0:
        recommendations.append(
            RecommendationResult(
                severity="info",
                title="Hold & Win Not Contributing",
                description=(
                    "Hold & Win contributed 0% RTP. Reduce BONUS trigger threshold "
                    "or increase BONUS symbol density on reel strips."
                ),
            ),
        )

    fs_triggers = result.feature_trigger_counts.get("FREE_SPINS", 0)
    if result.spin_count > 0:
        fs_freq = fs_triggers / result.spin_count
        if fs_freq > 0.5:
            recommendations.append(
                RecommendationResult(
                    severity="warning",
                    title="High Feature Frequency",
                    description=(
                        f"FREE_SPINS triggers on {fs_freq * 100:.1f}% of spins. "
                        "Feature frequency may be too high for production gameplay."
                    ),
                ),
            )

    if chart.jackpot > chart.total_rtp * 0.5 and chart.jackpot > 10.0:
        recommendations.append(
            RecommendationResult(
                severity="critical",
                title="Jackpot Dominates RTP",
                description=(
                    f"Jackpot contributes {chart.jackpot:.1f}% of total RTP. "
                    "Review jackpot tier multipliers and Hold & Win entry thresholds."
                ),
            ),
        )

    return tuple(recommendations)
