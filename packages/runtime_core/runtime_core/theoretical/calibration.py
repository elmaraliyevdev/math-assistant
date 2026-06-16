"""Calibration engine comparing theoretical, simulated, and target RTP."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.theoretical.models import (
    CalibrationRecommendation,
    CalibrationResult,
    FeatureProbability,
    TheoreticalRtpResult,
)


def calibrate_rtp(
    *,
    theoretical_rtp: TheoreticalRtpResult,
    simulated_rtp: float | None = None,
    target_rtp: float | None = None,
    tolerance: float | None = None,
) -> CalibrationResult:
    """Compare theoretical, simulated, and target RTP values."""
    theory_percent = theoretical_rtp.total_rtp * 100.0
    simulated_percent = (
        round(simulated_rtp * 100.0, 4) if simulated_rtp is not None else None
    )
    target_delta = None
    if target_rtp is not None:
        target_delta = round(theory_percent - target_rtp, 4)

    theory_vs_simulation_delta = None
    if simulated_percent is not None:
        theory_vs_simulation_delta = round(simulated_percent - theory_percent, 4)

    within_tolerance = None
    if target_rtp is not None and tolerance is not None:
        reference = simulated_percent if simulated_percent is not None else theory_percent
        within_tolerance = abs(reference - target_rtp) <= tolerance

    return CalibrationResult(
        targetRtp=target_rtp,
        theoreticalRtp=round(theory_percent, 4),
        simulatedRtp=simulated_percent,
        targetDelta=target_delta,
        theoryVsSimulationDelta=theory_vs_simulation_delta,
        withinTolerance=within_tolerance,
        tolerance=tolerance,
    )


def generate_calibration_recommendations(
    game: GameVersion,
    calibration: CalibrationResult,
    theoretical: TheoreticalRtpResult,
    feature_probabilities: tuple[FeatureProbability, ...],
) -> tuple[CalibrationRecommendation, ...]:
    """Produce actionable tuning suggestions with expected RTP impact."""
    recommendations: list[CalibrationRecommendation] = []

    if calibration.target_rtp is not None and calibration.target_delta is not None:
        gap = calibration.target_delta
        if gap < -0.01:
            recommendations.extend(
                _recommendations_to_raise_rtp(game, abs(gap), theoretical),
            )
        elif gap > 0.01:
            recommendations.extend(
                _recommendations_to_lower_rtp(game, gap, theoretical, feature_probabilities),
            )

    if calibration.theory_vs_simulation_delta is not None:
        sim_gap = calibration.theory_vs_simulation_delta
        if abs(sim_gap) > 0.02:
            recommendations.append(
                CalibrationRecommendation(
                    severity="warning",
                    category="simulation_validation",
                    action=(
                        "Re-run simulation with higher spin count or verify reel "
                        "strip weights match the canonical game version."
                    ),
                    expectedRtpImpact=(
                        f"Closing the {abs(sim_gap) * 100:.2f} percentage-point "
                        "theory vs simulation gap improves certification confidence."
                    ),
                ),
            )

    return tuple(recommendations)


def _recommendations_to_raise_rtp(
    game: GameVersion,
    gap: float,
    theoretical: TheoreticalRtpResult,
) -> list[CalibrationRecommendation]:
    results: list[CalibrationRecommendation] = []
    pays = game.paytable.pays
    if pays:
        top = max(pays, key=lambda entry: entry.multiplier)
        suggested = int(round(float(top.multiplier) * 1.2))
        impact = min(gap * 100.0 * 0.4, 5.0)
        results.append(
            CalibrationRecommendation(
                severity="warning",
                category="paytable",
                action=(
                    f"Increase {top.symbol_id} {top.count}OAK multiplier from "
                    f"{top.multiplier}x to {suggested}x."
                ),
                expectedRtpImpact=(
                    f"Estimated +{impact:.1f} percentage points toward target RTP "
                    f"(current base theoretical RTP {theoretical.base_rtp * 100:.2f}%)."
                ),
            ),
        )

    scatter_specs: list[dict] = []
    main = game.state_machines.get("main")
    if main is not None:
        base = main.states.get("BASE")
        if base is not None:
            raw = base.plugin_config.get("scatterTriggers", [])
            if isinstance(raw, list):
                scatter_specs = [item for item in raw if isinstance(item, dict)]
    if scatter_specs:
        spec = scatter_specs[0]
        award = spec.get("awardSpins") or spec.get("freeSpinsAward")
        if isinstance(award, int) and award > 8:
            reduced = max(8, int(round(award * 0.8)))
            results.append(
                CalibrationRecommendation(
                    severity="info",
                    category="feature_awards",
                    action=f"Reduce Free Spins awards from {award} to {reduced}.",
                    expectedRtpImpact=(
                        f"Estimated +{min(gap * 100.0 * 0.25, 3.0):.1f} percentage points "
                        "by lowering feature RTP contribution."
                    ),
                ),
            )

    return results


def _recommendations_to_lower_rtp(
    game: GameVersion,
    gap: float,
    theoretical: TheoreticalRtpResult,
    feature_probabilities: tuple[FeatureProbability, ...],
) -> list[CalibrationRecommendation]:
    results: list[CalibrationRecommendation] = []

    for feature in feature_probabilities:
        if feature.trigger == "FREE_SPINS" and feature.probability > 0.01:
            results.append(
                CalibrationRecommendation(
                    severity="warning",
                    category="reel_strips",
                    action="Reduce scatter frequency on reel 1 by 20%.",
                    expectedRtpImpact=(
                        f"Estimated -{min(gap * 100.0 * 0.3, 4.0):.1f} percentage points "
                        "by lowering FREE_SPINS trigger rate."
                    ),
                ),
            )
            break

    for machine in game.state_machines.values():
        for state in machine.states.values():
            tiers = state.plugin_config.get("jackpotTiers")
            if not isinstance(tiers, dict):
                continue
            grand = tiers.get("grand")
            if isinstance(grand, (int, float)) and grand > 100:
                suggested = max(100, int(round(grand * 0.6)))
                results.append(
                    CalibrationRecommendation(
                        severity="warning",
                        category="jackpot",
                        action=f"Lower jackpot tier GRAND from {int(grand)}x to {suggested}x.",
                        expectedRtpImpact=(
                            f"Estimated -{min(gap * 100.0 * 0.35, 6.0):.1f} percentage points "
                            "from reduced jackpot exposure."
                        ),
                    ),
                )
                break

    pays = game.paytable.pays
    if pays and not results:
        top = max(pays, key=lambda entry: entry.multiplier)
        suggested = max(1, int(round(float(top.multiplier) * 0.85)))
        results.append(
            CalibrationRecommendation(
                severity="info",
                category="paytable",
                action=(
                    f"Reduce {top.symbol_id} {top.count}OAK multiplier from "
                    f"{top.multiplier}x to {suggested}x."
                ),
                expectedRtpImpact=(
                    f"Estimated -{min(gap * 100.0 * 0.4, 5.0):.1f} percentage points "
                    f"(current base theoretical RTP {theoretical.base_rtp * 100:.2f}%)."
                ),
            ),
        )

    return results
