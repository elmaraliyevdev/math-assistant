"""Design-aware recommendation engine tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from runtime_core.common.golden import load_golden_fixture_json
from runtime_core.domain.game_version import GameVersion
from runtime_core.mathematical.models import RtpDecompositionChart
from runtime_core.theoretical.calibration import (
    calibrate_rtp,
    generate_calibration_recommendations,
)
from runtime_core.theoretical.design_aware_recommendations import (
    build_certification_readiness_summary,
)
from runtime_core.theoretical.design_intent import detect_design_intent
from runtime_core.theoretical.models import TheoreticalRtpResult
from runtime_core.theoretical.theoretical_features import calculate_feature_probabilities
from runtime_core.theoretical.theoretical_rtp import calculate_theoretical_rtp


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _game(fixture: str = "fixture-01-base-5x3") -> GameVersion:
    payload = load_golden_fixture_json(fixture, repo_root=_repo_root())
    return GameVersion.model_validate(payload)


def _recommendations(
    game: GameVersion,
    *,
    chart: RtpDecompositionChart,
    target_rtp: float = 96.0,
) -> tuple:
    theoretical = TheoreticalRtpResult(
        totalRtp=chart.total_rtp / 100.0,
        baseRtp=chart.base / 100.0,
        scatterRtp=0.0,
        lineRtp=chart.base / 100.0,
        outcomeCount=1000,
        reelSetId="base_game",
    )
    calibration = calibrate_rtp(
        theoretical_rtp=theoretical,
        target_rtp=target_rtp,
        tolerance=0.1,
    )
    recommendations = generate_calibration_recommendations(
        game,
        calibration,
        theoretical,
        calculate_feature_probabilities(game),
        decomposition=chart,
    )
    return calibration, recommendations


def test_absent_feature_not_recommended_for_introduction() -> None:
    """Base-only game must not receive HOLD_AND_WIN / FREE_SPINS introduction guidance."""
    chart = RtpDecompositionChart(
        base=5.0,
        free_spins=45.0,
        hold_and_win=0.0,
        jackpot=0.0,
        total_rtp=50.0,
    )
    game = _game("fixture-01-base-5x3")
    intent = detect_design_intent(game)
    assert intent.has_hold_and_win is False

    _, recommendations = _recommendations(game, chart=chart)
    actions = " ".join(rec.action for rec in recommendations).lower()

    assert not any(rec.category == "hold_and_win" for rec in recommendations)
    assert "introduce calibrated hold" not in actions
    assert any(rec.category in {"base_rtp", "paytable_redesign"} for rec in recommendations)


def test_existing_features_can_be_tuned() -> None:
    chart = RtpDecompositionChart(
        base=30.0,
        free_spins=10.0,
        hold_and_win=5.0,
        jackpot=2.0,
        total_rtp=47.0,
    )
    game = _game("fixture-03-base-hold-win")
    intent = detect_design_intent(game)
    assert intent.has_hold_and_win is True

    _, recommendations = _recommendations(game, chart=chart)
    assert any(
        rec.category in {"hold_and_win", "base_rtp", "paytable_redesign"}
        for rec in recommendations
    )


def test_volatility_preserved_for_low_volatility_design() -> None:
    game = _game("fixture-01-base-5x3")
    game = game.model_copy(
        update={
            "metadata": game.metadata.model_copy(
                update={"volatility_target": "low"},
            ),
        },
    )
    theoretical = calculate_theoretical_rtp(game)
    calibration = calibrate_rtp(
        theoretical_rtp=theoretical,
        target_rtp=96.0,
        tolerance=0.1,
    )
    recommendations = generate_calibration_recommendations(
        game,
        calibration,
        theoretical,
        calculate_feature_probabilities(game),
    )

    assert not any(rec.category == "paytable" for rec in recommendations)
    for rec in recommendations:
        if rec.estimated_volatility_impact:
            assert "high increase" not in rec.estimated_volatility_impact.lower()


def test_exposure_constraints_respected_when_cap_enforced() -> None:
    chart = RtpDecompositionChart(
        base=30.0,
        free_spins=25.0,
        hold_and_win=10.0,
        jackpot=45.0,
        total_rtp=110.0,
    )
    game = _game("fixture-03-base-hold-win")
    _, recommendations = _recommendations(game, chart=chart)

    assert not any(
        rec.category == "jackpot" and "exceeds cap" in (rec.exposure_impact or "").lower()
        for rec in recommendations
    )
    for rec in recommendations:
        if rec.category in {"base_rtp", "paytable_redesign"} and rec.exposure_impact:
            assert "within cap" in rec.exposure_impact.lower()


def test_certification_readiness_summary_generated() -> None:
    game = _game()
    theoretical = calculate_theoretical_rtp(game)
    calibration = calibrate_rtp(
        theoretical_rtp=theoretical,
        target_rtp=96.0,
        tolerance=0.1,
    )
    recommendations = generate_calibration_recommendations(
        game,
        calibration,
        theoretical,
        calculate_feature_probabilities(game),
    )
    summary = build_certification_readiness_summary(calibration, recommendations)

    assert summary.certification_status == "certification_blocked"
    assert summary.blocking_issues
    assert summary.required_actions
    assert summary.estimated_iterations_remaining >= 1

    cleared_calibration = calibrate_rtp(
        theoretical_rtp=theoretical.model_copy(
            update={"total_rtp": 0.96, "base_rtp": 0.96, "line_rtp": 0.96},
        ),
        target_rtp=96.0,
        tolerance=1.0,
    )
    cleared_summary = build_certification_readiness_summary(
        cleared_calibration,
        (),
    )
    assert cleared_summary.estimated_iterations_remaining == 0
