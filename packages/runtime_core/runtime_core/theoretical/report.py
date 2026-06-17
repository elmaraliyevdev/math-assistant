"""Theoretical analysis and export report helpers."""

from __future__ import annotations

import json
from typing import Any

from runtime_core.common.version import ENGINE_VERSION
from runtime_core.domain.game_version import GameVersion
from runtime_core.mathematical.models import RtpDecompositionChart
from runtime_core.theoretical.calibration import (
    calibrate_rtp,
    generate_calibration_recommendations,
)
from runtime_core.theoretical.certification import build_certification_report
from runtime_core.theoretical.design_aware_recommendations import (
    build_certification_readiness_summary,
)
from runtime_core.theoretical.discrepancy import analyze_discrepancies
from runtime_core.theoretical.models import (
    CertificationReport,
    TheoreticalAnalysis,
)
from runtime_core.theoretical.theoretical_features import calculate_feature_probabilities
from runtime_core.theoretical.theoretical_rtp import calculate_theoretical_rtp


def build_theoretical_analysis(
    game: GameVersion,
    *,
    reel_set_id: str | None = None,
    total_bet_minor_units: int | None = None,
) -> TheoreticalAnalysis:
    """Compute theoretical RTP and feature trigger probabilities."""
    rtp = calculate_theoretical_rtp(
        game,
        reel_set_id=reel_set_id,
        total_bet_minor_units=total_bet_minor_units,
    )
    feature_probabilities = calculate_feature_probabilities(game)
    return TheoreticalAnalysis(
        rtp=rtp,
        featureProbabilities=feature_probabilities,
        engineVersion=ENGINE_VERSION,
    )


def build_calibration_report(
    game: GameVersion,
    *,
    simulated_rtp: float | None = None,
    rtp_variance: float | None = None,
    simulated_feature_frequencies: dict[str, float] | None = None,
    total_bet_minor_units: int | None = None,
    reel_set_id: str | None = None,
    tolerance: float | None = None,
    decomposition: RtpDecompositionChart | None = None,
) -> dict[str, Any]:
    """Return calibration payload with recommendations and discrepancy analysis."""
    theoretical = calculate_theoretical_rtp(
        game,
        reel_set_id=reel_set_id,
        total_bet_minor_units=total_bet_minor_units,
    )
    feature_probabilities = calculate_feature_probabilities(game)

    target_rtp = None
    resolved_tolerance = tolerance
    if game.metadata.rtp_target is not None:
        target_rtp = game.metadata.rtp_target.percent
        if resolved_tolerance is None:
            resolved_tolerance = game.metadata.rtp_target.tolerance

    calibration = calibrate_rtp(
        theoretical_rtp=theoretical,
        simulated_rtp=simulated_rtp,
        target_rtp=target_rtp,
        tolerance=resolved_tolerance,
    )
    discrepancy = analyze_discrepancies(
        calibration,
        feature_probabilities=feature_probabilities,
        simulated_feature_frequencies=simulated_feature_frequencies,
        rtp_variance=rtp_variance,
    )
    recommendations = generate_calibration_recommendations(
        game,
        calibration,
        theoretical,
        feature_probabilities,
        decomposition=decomposition,
    )
    readiness = build_certification_readiness_summary(calibration, recommendations)

    return {
        "theoreticalRtp": theoretical.model_dump(mode="json", by_alias=True),
        "featureProbabilities": [
            item.model_dump(mode="json", by_alias=True)
            for item in feature_probabilities
        ],
        "calibration": calibration.model_dump(mode="json", by_alias=True),
        "discrepancy": discrepancy.model_dump(mode="json", by_alias=True),
        "recommendations": [
            item.model_dump(mode="json", by_alias=True) for item in recommendations
        ],
        "certificationReadiness": readiness.model_dump(mode="json", by_alias=True),
        "engineVersion": ENGINE_VERSION,
    }


def export_certification_json(report: CertificationReport) -> bytes:
    """Serialize a certification report to JSON bytes."""
    payload = report.model_dump(mode="json", by_alias=True)
    return json.dumps(payload, indent=2).encode("utf-8")


def export_certification_pdf(report: CertificationReport) -> bytes:
    """Render a plain-text certification report suitable for PDF download."""
    lines = [
        "Certification Mathematics Report",
        f"Game: {report.game_title}",
        f"Game Version: {report.game_version_id}",
        f"Engine: {report.engine_version}",
        "",
        "RTP Summary",
        f"  Target RTP: {_format_percent(report.target_rtp, already_percent=True)}",
        f"  Theoretical RTP: {_format_percent(report.theoretical_rtp.total_rtp)}",
        f"    Base / Line / Scatter: "
        f"{_format_percent(report.theoretical_rtp.base_rtp)} / "
        f"{_format_percent(report.theoretical_rtp.line_rtp)} / "
        f"{_format_percent(report.theoretical_rtp.scatter_rtp)}",
        f"  Simulated RTP: {_format_percent(report.simulated_rtp, already_percent=True)}",
        f"  RTP Variance: {report.rtp_variance if report.rtp_variance is not None else 'n/a'}",
        "",
        "Feature Probabilities",
    ]
    for feature in report.feature_probabilities:
        one_in = feature.one_in_x if feature.one_in_x is not None else "n/a"
        lines.append(
            f"  {feature.trigger}: {feature.probability:.6f} (1 in {one_in})",
        )

    lines.extend(
        [
            "",
            "Exposure",
            f"  Max Win: {report.exposure.max_win_minor_units} minor units",
            f"  Max Multiplier: {report.exposure.max_win_multiplier}",
            f"  Cap Scope: {report.exposure.cap_scope}",
        ],
    )

    if report.discrepancy is not None:
        lines.extend(["", "Discrepancy Analysis", f"  {report.discrepancy.summary}"])
        for item in report.discrepancy.items:
            lines.append(
                f"  - {item.metric}: delta={item.delta} status={item.status}",
            )

    if report.recommendations:
        lines.append("")
        lines.append("Recommendations")
        for rec in report.recommendations:
            lines.append(f"  [{rec.severity}] {rec.action}")
            lines.append(f"    Impact: {rec.expected_rtp_impact}")

    return "\n".join(lines).encode("utf-8")


def _format_percent(value: float | None, *, already_percent: bool = False) -> str:
    if value is None:
        return "n/a"
    if already_percent:
        return f"{value:.4f}%"
    return f"{value * 100:.4f}%"
