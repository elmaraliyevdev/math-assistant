"""Calibration engine comparing theoretical, simulated, and target RTP."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.mathematical.models import RtpDecompositionChart
from runtime_core.theoretical.design_aware_recommendations import (
    apply_design_aware_constraints,
)
from runtime_core.theoretical.discrepancy_severity import (
    DEFAULT_CERTIFICATION_BLOCK_THRESHOLD_PP,
    DiscrepancySeverity,
    classify_rtp_gap_pp,
    resolve_certification_status,
)
from runtime_core.theoretical.models import (
    CalibrationRecommendation,
    CalibrationResult,
    FeatureProbability,
    TheoreticalRtpResult,
)
from runtime_core.theoretical.rtp_decomposition_analysis import (
    build_decomposition_lower_recommendations,
    build_decomposition_raise_recommendations,
    is_balanced_near_target,
    resolve_decomposition_chart,
)


def calibrate_rtp(
    *,
    theoretical_rtp: TheoreticalRtpResult,
    simulated_rtp: float | None = None,
    target_rtp: float | None = None,
    tolerance: float | None = None,
    certification_block_threshold_pp: float = DEFAULT_CERTIFICATION_BLOCK_THRESHOLD_PP,
) -> CalibrationResult:
    """Compare theoretical, simulated, and target RTP values."""
    theory_percent = theoretical_rtp.total_rtp * 100.0
    simulated_percent = (
        round(simulated_rtp * 100.0, 4) if simulated_rtp is not None else None
    )
    target_delta = None
    rtp_gap_pp = None
    discrepancy_severity = None
    certification_status = None
    if target_rtp is not None:
        target_delta = round(theory_percent - target_rtp, 4)
        rtp_gap_pp = round(abs(target_delta), 4)
        discrepancy_severity = classify_rtp_gap_pp(target_delta).value
        certification_status = resolve_certification_status(
            target_delta,
            block_threshold_pp=certification_block_threshold_pp,
        )

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
        rtpGapPp=rtp_gap_pp,
        discrepancySeverity=discrepancy_severity,
        certificationStatus=certification_status,
        certificationBlockThresholdPp=certification_block_threshold_pp,
    )


def generate_calibration_recommendations(
    game: GameVersion,
    calibration: CalibrationResult,
    theoretical: TheoreticalRtpResult,
    feature_probabilities: tuple[FeatureProbability, ...],
    *,
    certification_block_threshold_pp: float | None = None,
    decomposition: RtpDecompositionChart | None = None,
    allow_volatility_class_change: bool = False,
) -> tuple[CalibrationRecommendation, ...]:
    """Produce actionable tuning suggestions with expected RTP impact."""
    block_threshold = (
        certification_block_threshold_pp
        if certification_block_threshold_pp is not None
        else calibration.certification_block_threshold_pp
        if calibration.certification_block_threshold_pp is not None
        else DEFAULT_CERTIFICATION_BLOCK_THRESHOLD_PP
    )
    chart = resolve_decomposition_chart(
        theoretical=theoretical,
        decomposition=decomposition,
    )
    recommendations: list[CalibrationRecommendation] = []

    if calibration.target_rtp is not None and calibration.target_delta is not None:
        gap_signed = calibration.target_delta
        gap_pp = abs(gap_signed)
        severity = classify_rtp_gap_pp(gap_signed)
        target_percent = calibration.target_rtp

        if gap_pp > 0.01:
            if gap_signed < 0:
                recommendations.extend(
                    _recommendations_to_raise_rtp(
                        game,
                        gap_pp=gap_pp,
                        severity=severity,
                        theoretical=theoretical,
                        target_percent=target_percent,
                        block_threshold_pp=block_threshold,
                        chart=chart,
                    ),
                )
            else:
                recommendations.extend(
                    _recommendations_to_lower_rtp(
                        game,
                        gap_pp=gap_pp,
                        severity=severity,
                        theoretical=theoretical,
                        target_percent=target_percent,
                        block_threshold_pp=block_threshold,
                        chart=chart,
                    ),
                )
        elif is_balanced_near_target(chart, target_percent, gap_pp=gap_pp):
            recommendations.append(
                CalibrationRecommendation(
                    severity="info",
                    category="status",
                    action=(
                        "RTP decomposition is balanced relative to the target. "
                        "No component-level tuning is required."
                    ),
                    expectedRtpImpact=(
                        f"BASE {chart.base:.2f}%, FREE_SPINS {chart.free_spins:.2f}%, "
                        f"HOLD_AND_WIN {chart.hold_and_win:.2f}%, JACKPOT {chart.jackpot:.2f}% "
                        "are within expected ranges."
                    ),
                    estimatedRtpContributionPp=0.0,
                    priority=1,
                    discrepancySeverity="minor",
                ),
            )

    recommendations.extend(
        _simulation_validation_recommendations(calibration),
    )

    recommendations.sort(key=_recommendation_sort_key, reverse=True)
    filtered = apply_design_aware_constraints(
        tuple(recommendations),
        game=game,
        theoretical=theoretical,
        allow_volatility_class_change=allow_volatility_class_change,
    )
    if (
        calibration.target_delta is not None
        and calibration.target_rtp is not None
        and abs(calibration.target_delta) < 2.0
        and classify_rtp_gap_pp(calibration.target_delta) == DiscrepancySeverity.MINOR
        and not any(
            item.estimated_rtp_contribution_pp > 0
            for item in filtered
            if item.category not in {"certification", "status", "simulation_validation"}
        )
    ):
        gap_pp = abs(calibration.target_delta)
        minor = _minor_raise_recommendations(
            game,
            gap_pp=gap_pp,
            severity=DiscrepancySeverity.MINOR,
            theoretical=theoretical,
        )
        if minor:
            merged = list(filtered) + minor
            merged.sort(key=_recommendation_sort_key, reverse=True)
            filtered = apply_design_aware_constraints(
                tuple(merged),
                game=game,
                theoretical=theoretical,
                allow_volatility_class_change=allow_volatility_class_change,
            )
    return filtered


def _recommendation_sort_key(item: CalibrationRecommendation) -> tuple[float, float, float]:
    """Certification notices first; actionable items by estimated RTP impact."""
    if item.category == "certification":
        return (10_000.0, item.priority, item.estimated_rtp_contribution_pp)
    return (item.estimated_rtp_contribution_pp, item.priority, 0.0)


def _simulation_validation_recommendations(
    calibration: CalibrationResult,
) -> list[CalibrationRecommendation]:
    if calibration.theory_vs_simulation_delta is None:
        return []

    sim_gap = calibration.theory_vs_simulation_delta
    if abs(sim_gap) <= 0.02:
        return []

    return [
        CalibrationRecommendation(
            severity="warning",
            category="simulation_validation",
            action=(
                "Re-run simulation with higher spin count or verify reel "
                "strip weights match the canonical game version."
            ),
            expectedRtpImpact=(
                f"Closing the {abs(sim_gap):.2f} percentage-point theory vs "
                "simulation gap improves certification confidence."
            ),
            estimatedRtpContributionPp=abs(sim_gap),
            priority=1,
            discrepancySeverity=classify_rtp_gap_pp(sim_gap).value,
        ),
    ]


def _certification_blocked_notice(
    *,
    gap_pp: float,
    severity: DiscrepancySeverity,
    target_percent: float,
    theoretical_percent: float,
    block_threshold_pp: float,
) -> CalibrationRecommendation:
    return CalibrationRecommendation(
        severity="critical",
        category="certification",
        action=(
            f"Certification blocked: theoretical RTP {theoretical_percent:.2f}% is "
            f"{gap_pp:.2f} percentage points from the {target_percent:.2f}% target "
            f"(threshold {block_threshold_pp:.0f} pp). Micro-adjustments are "
            "insufficient — revise mathematics systemically before certification."
        ),
        expectedRtpImpact=(
            f"Requires closing a {gap_pp:.2f} percentage-point gap through paytable "
            "and feature redesign, not incremental multiplier tweaks."
        ),
        estimatedRtpContributionPp=0.0,
        priority=100,
        discrepancySeverity=severity.value,
    )


def _recommendations_to_raise_rtp(
    game: GameVersion,
    *,
    gap_pp: float,
    severity: DiscrepancySeverity,
    theoretical: TheoreticalRtpResult,
    target_percent: float,
    block_threshold_pp: float,
    chart: RtpDecompositionChart,
) -> list[CalibrationRecommendation]:
    theoretical_percent = theoretical.total_rtp * 100.0
    results: list[CalibrationRecommendation] = []

    if severity == DiscrepancySeverity.CRITICAL:
        results.append(
            _certification_blocked_notice(
                gap_pp=gap_pp,
                severity=severity,
                target_percent=target_percent,
                theoretical_percent=theoretical_percent,
                block_threshold_pp=block_threshold_pp,
            ),
        )

    if is_balanced_near_target(chart, target_percent, gap_pp=gap_pp):
        if severity == DiscrepancySeverity.MINOR:
            results.extend(
                _minor_raise_recommendations(
                    game,
                    gap_pp=gap_pp,
                    severity=severity,
                    theoretical=theoretical,
                ),
            )
        return results

    results.extend(
        build_decomposition_raise_recommendations(
            chart=chart,
            target_rtp=target_percent,
            gap_pp=gap_pp,
            severity=severity,
            game=game,
            theoretical=theoretical,
        ),
    )

    if severity == DiscrepancySeverity.MINOR and not results:
        results.extend(
            _minor_raise_recommendations(
                game,
                gap_pp=gap_pp,
                severity=severity,
                theoretical=theoretical,
            ),
        )

    return results


def _recommendations_to_lower_rtp(
    game: GameVersion,
    *,
    gap_pp: float,
    severity: DiscrepancySeverity,
    theoretical: TheoreticalRtpResult,
    target_percent: float,
    block_threshold_pp: float,
    chart: RtpDecompositionChart,
) -> list[CalibrationRecommendation]:
    theoretical_percent = theoretical.total_rtp * 100.0
    results: list[CalibrationRecommendation] = []

    if severity == DiscrepancySeverity.CRITICAL:
        results.append(
            _certification_blocked_notice(
                gap_pp=gap_pp,
                severity=severity,
                target_percent=target_percent,
                theoretical_percent=theoretical_percent,
                block_threshold_pp=block_threshold_pp,
            ),
        )

    if is_balanced_near_target(chart, target_percent, gap_pp=gap_pp):
        return results

    results.extend(
        build_decomposition_lower_recommendations(
            chart=chart,
            target_rtp=target_percent,
            gap_pp=gap_pp,
            severity=severity,
            game=game,
            theoretical=theoretical,
        ),
    )
    return results


def _minor_raise_recommendations(
    game: GameVersion,
    *,
    gap_pp: float,
    severity: DiscrepancySeverity,
    theoretical: TheoreticalRtpResult,
) -> list[CalibrationRecommendation]:
    pays = game.paytable.pays
    if not pays:
        return []

    top = max(pays, key=lambda entry: entry.multiplier)
    suggested = int(round(float(top.multiplier) * 1.05))
    impact = min(
        _estimate_paytable_multiplier_impact_pp(
            theoretical,
            current_multiplier=float(top.multiplier),
            suggested_multiplier=float(suggested),
        ),
        gap_pp,
    )
    return [
        CalibrationRecommendation(
            severity="info",
            category="paytable",
            action=(
                f"Increase {top.symbol_id} {top.count}OAK multiplier from "
                f"{top.multiplier}x to {suggested}x."
            ),
            expectedRtpImpact=(
                f"Estimated +{impact:.2f} percentage points toward target RTP "
                f"(current theoretical RTP {theoretical.total_rtp * 100:.2f}%)."
            ),
            estimatedRtpContributionPp=impact,
            priority=25,
            discrepancySeverity=severity.value,
        ),
    ]


def _estimate_paytable_multiplier_impact_pp(
    theoretical: TheoreticalRtpResult,
    *,
    current_multiplier: float,
    suggested_multiplier: float,
    top_symbol_weight: float = 0.35,
) -> float:
    if current_multiplier <= 0:
        return 0.0
    ratio_delta = suggested_multiplier / current_multiplier - 1.0
    return round(max(0.0, theoretical.line_rtp * 100.0 * ratio_delta * top_symbol_weight), 2)
