"""Recommendation quality tests for severity-aware calibration guidance."""

from __future__ import annotations

from pathlib import Path

import pytest
from runtime_core.common.golden import load_golden_fixture_json
from runtime_core.domain.game_version import GameVersion
from runtime_core.theoretical.calibration import (
    calibrate_rtp,
    generate_calibration_recommendations,
)
from runtime_core.theoretical.discrepancy_severity import (
    DiscrepancySeverity,
    classify_rtp_gap_pp,
)
from runtime_core.theoretical.theoretical_features import calculate_feature_probabilities
from runtime_core.theoretical.theoretical_rtp import calculate_theoretical_rtp


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _game() -> GameVersion:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    return GameVersion.model_validate(payload)


def _recommendations_for_target(target_rtp: float) -> tuple:
    game = _game()
    theoretical = calculate_theoretical_rtp(game)
    features = calculate_feature_probabilities(game)
    calibration = calibrate_rtp(
        theoretical_rtp=theoretical,
        target_rtp=target_rtp,
        tolerance=0.1,
    )
    return (
        calibration,
        generate_calibration_recommendations(
            game,
            calibration,
            theoretical,
            features,
        ),
    )


def test_severity_classification_thresholds() -> None:
    assert classify_rtp_gap_pp(1.5) == DiscrepancySeverity.MINOR
    assert classify_rtp_gap_pp(-5.0) == DiscrepancySeverity.MODERATE
    assert classify_rtp_gap_pp(16.0) == DiscrepancySeverity.MAJOR
    assert classify_rtp_gap_pp(-90.88) == DiscrepancySeverity.CRITICAL


def test_critical_gap_blocks_certification_and_avoids_micro_adjustments() -> None:
    calibration, recommendations = _recommendations_for_target(96.0)

    assert calibration.discrepancy_severity == "critical"
    assert calibration.certification_status == "certification_blocked"
    assert calibration.rtp_gap_pp == pytest.approx(90.88, abs=0.1)

    actions = " ".join(rec.action for rec in recommendations)
    assert "Certification blocked" in actions
    assert any(rec.category in {"base_rtp", "paytable_redesign"} for rec in recommendations)
    assert "120x" not in actions
    assert all(rec.estimated_rtp_contribution_pp >= 0 for rec in recommendations)
    assert recommendations[0].category == "certification"

    contributions = [
        rec.estimated_rtp_contribution_pp
        for rec in recommendations
        if rec.estimated_rtp_contribution_pp > 0
    ]
    assert contributions == sorted(contributions, reverse=True)


def test_major_gap_recommends_systemic_changes_without_single_symbol_tweak() -> None:
    game = _game()
    theoretical = calculate_theoretical_rtp(game)
    adjusted = theoretical.model_copy(
        update={"total_rtp": 0.80, "base_rtp": 0.80, "line_rtp": 0.80},
    )
    calibration = calibrate_rtp(
        theoretical_rtp=adjusted,
        target_rtp=96.0,
        tolerance=0.1,
    )
    recommendations = generate_calibration_recommendations(
        game,
        calibration,
        adjusted,
        calculate_feature_probabilities(game),
    )

    assert calibration.discrepancy_severity == "major"
    assert calibration.certification_status == "review_required"
    actions = " ".join(rec.action for rec in recommendations)
    assert any(
        rec.category in {"base_rtp", "paytable_redesign", "hold_and_win"}
        for rec in recommendations
    )
    assert "120x" not in actions
    assert all(rec.expected_rtp_impact for rec in recommendations)


def test_minor_gap_allows_fine_tuning_with_realistic_impact() -> None:
    game = _game()
    theoretical = calculate_theoretical_rtp(game)
    adjusted = theoretical.model_copy(
        update={"total_rtp": 0.959, "base_rtp": 0.959, "line_rtp": 0.959},
    )
    calibration = calibrate_rtp(
        theoretical_rtp=adjusted,
        target_rtp=96.0,
        tolerance=0.1,
    )
    recommendations = generate_calibration_recommendations(
        game,
        calibration,
        adjusted,
        calculate_feature_probabilities(game),
    )

    assert calibration.discrepancy_severity == "minor"
    assert calibration.certification_status == "cleared"
    assert calibration.rtp_gap_pp == pytest.approx(0.1, abs=0.01)
    assert recommendations
    top = recommendations[0]
    assert top.estimated_rtp_contribution_pp <= calibration.rtp_gap_pp
    assert top.estimated_rtp_contribution_pp < 1.0


def test_five_percent_game_targeting_ninety_six_percent() -> None:
    """Regression: 5.12% theoretical game targeting 96% must not suggest +5% multiplier tweaks."""
    calibration, recommendations = _recommendations_for_target(96.0)

    assert calibration.theoretical_rtp == pytest.approx(5.12, abs=0.01)
    assert calibration.target_delta == pytest.approx(-90.88, abs=0.1)
    assert not any("multiplier from 100x to 120x" in rec.action for rec in recommendations)
    paytable = [
        rec
        for rec in recommendations
        if rec.category in {"paytable", "paytable_redesign", "base_rtp"}
    ]
    assert paytable
    assert paytable[0].estimated_rtp_contribution_pp > 0


def test_recommendations_sorted_by_highest_impact_first() -> None:
    _, recommendations = _recommendations_for_target(96.0)
    impacts = [
        rec.estimated_rtp_contribution_pp
        for rec in recommendations
        if rec.estimated_rtp_contribution_pp > 0
    ]
    assert impacts == sorted(impacts, reverse=True)
