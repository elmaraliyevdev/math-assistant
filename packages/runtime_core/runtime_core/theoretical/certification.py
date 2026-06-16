"""Certification report assembly."""

from __future__ import annotations

import uuid

from runtime_core.common.version import ENGINE_VERSION
from runtime_core.domain.game_version import GameVersion
from runtime_core.theoretical.calibration import (
    calibrate_rtp,
    generate_calibration_recommendations,
)
from runtime_core.theoretical.discrepancy import analyze_discrepancies
from runtime_core.theoretical.models import (
    CertificationExposureStats,
    CertificationReport,
)
from runtime_core.theoretical.theoretical_features import calculate_feature_probabilities
from runtime_core.theoretical.theoretical_rtp import calculate_theoretical_rtp


def build_certification_report(
    game: GameVersion,
    *,
    simulated_rtp: float | None = None,
    rtp_variance: float | None = None,
    simulated_feature_frequencies: dict[str, float] | None = None,
    total_bet_minor_units: int | None = None,
    reel_set_id: str | None = None,
    tolerance: float | None = None,
) -> CertificationReport:
    """Assemble a certification-ready mathematics report."""
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
    )

    simulated_percent = (
        round(simulated_rtp * 100.0, 4) if simulated_rtp is not None else None
    )

    return CertificationReport(
        gameVersionId=game.game_version.id,
        gameTitle=game.metadata.title,
        targetRtp=target_rtp,
        theoreticalRtp=theoretical,
        simulatedRtp=simulated_percent,
        rtpVariance=rtp_variance,
        featureProbabilities=feature_probabilities,
        exposure=CertificationExposureStats(
            maxWinMinorUnits=game.exposure.max_win_minor_units,
            maxWinMultiplier=game.exposure.max_win_multiplier,
            capScope=game.exposure.cap_scope,
        ),
        calibration=calibration,
        discrepancy=discrepancy,
        recommendations=recommendations,
        engineVersion=ENGINE_VERSION,
    )


def certification_report_document_id() -> str:
    """Return a unique document identifier for exported certification reports."""
    return str(uuid.uuid4())
