"""Discrepancy analysis between theoretical and simulated mathematics."""

from __future__ import annotations

from runtime_core.theoretical.models import (
    CalibrationResult,
    DiscrepancyAnalysis,
    DiscrepancyItem,
    FeatureProbability,
)


def analyze_discrepancies(
    calibration: CalibrationResult,
    *,
    feature_probabilities: tuple[FeatureProbability, ...] = (),
    simulated_feature_frequencies: dict[str, float] | None = None,
    rtp_variance: float | None = None,
) -> DiscrepancyAnalysis:
    """Compare theoretical, simulated, and target metrics."""
    items: list[DiscrepancyItem] = []

    if calibration.target_rtp is not None and calibration.theoretical_rtp is not None:
        delta = calibration.theoretical_rtp - calibration.target_rtp
        items.append(
            DiscrepancyItem(
                metric="theoretical_vs_target_rtp",
                theoretical=calibration.theoretical_rtp,
                target=calibration.target_rtp,
                delta=round(delta, 4),
                status=_status_for_delta(delta, calibration.tolerance),
            ),
        )

    if (
        calibration.simulated_rtp is not None
        and calibration.theoretical_rtp is not None
    ):
        delta = calibration.simulated_rtp - calibration.theoretical_rtp
        items.append(
            DiscrepancyItem(
                metric="simulation_vs_theoretical_rtp",
                theoretical=calibration.theoretical_rtp,
                simulated=calibration.simulated_rtp,
                delta=round(delta, 4),
                status=_status_for_delta(delta, calibration.tolerance),
            ),
        )

    if calibration.target_rtp is not None and calibration.simulated_rtp is not None:
        delta = calibration.simulated_rtp - calibration.target_rtp
        items.append(
            DiscrepancyItem(
                metric="simulation_vs_target_rtp",
                simulated=calibration.simulated_rtp,
                target=calibration.target_rtp,
                delta=round(delta, 4),
                status=_status_for_delta(delta, calibration.tolerance),
            ),
        )

    if rtp_variance is not None:
        items.append(
            DiscrepancyItem(
                metric="rtp_variance",
                simulated=rtp_variance,
                delta=rtp_variance,
                status="info",
            ),
        )

    simulated_features = simulated_feature_frequencies or {}
    for feature in feature_probabilities:
        observed = simulated_features.get(feature.trigger)
        if observed is None:
            continue
        delta = observed - feature.probability
        items.append(
            DiscrepancyItem(
                metric=f"feature_frequency:{feature.trigger}",
                theoretical=feature.probability,
                simulated=observed,
                delta=round(delta, 6),
                status=_status_for_delta(delta * 100.0, 5.0),
            ),
        )

    summary = _build_summary(items, calibration)
    return DiscrepancyAnalysis(items=tuple(items), summary=summary)


def _status_for_delta(delta: float, tolerance: float | None) -> str:
    limit = tolerance if tolerance is not None else 1.0
    if abs(delta) <= limit:
        return "ok"
    if abs(delta) <= limit * 2:
        return "warning"
    return "critical"


def _build_summary(items: tuple[DiscrepancyItem, ...], calibration: CalibrationResult) -> str:
    critical = sum(1 for item in items if item.status == "critical")
    warnings = sum(1 for item in items if item.status == "warning")
    if critical > 0:
        return (
            f"{critical} critical discrepancy(ies) detected between theoretical, "
            "simulated, and target mathematics."
        )
    if warnings > 0:
        return (
            f"{warnings} metric(s) outside tolerance; review calibration "
            "recommendations before certification."
        )
    if calibration.within_tolerance is True:
        return "Theoretical and simulated RTP are within configured tolerance."
    if calibration.within_tolerance is False:
        return "RTP metrics diverge from target beyond configured tolerance."
    return "Discrepancy analysis complete."
