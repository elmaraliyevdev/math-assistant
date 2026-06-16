"""Edge-case coverage for theoretical mathematics package."""

from __future__ import annotations

from pathlib import Path

import pytest
from runtime_core.common.golden import load_golden_fixture_json
from runtime_core.domain.game_version import GameVersion
from runtime_core.theoretical.calibration import (
    calibrate_rtp,
    generate_calibration_recommendations,
)
from runtime_core.theoretical.discrepancy import analyze_discrepancies
from runtime_core.theoretical.models import CalibrationResult, TheoreticalRtpResult
from runtime_core.theoretical.report import (
    build_calibration_report,
    build_theoretical_analysis,
    export_certification_json,
    export_certification_pdf,
)
from runtime_core.theoretical.theoretical_features import calculate_feature_probabilities
from runtime_core.theoretical.theoretical_rtp import calculate_theoretical_rtp


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def test_build_theoretical_analysis_wrapper() -> None:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    analysis = build_theoretical_analysis(game)
    assert analysis.engine_version
    assert analysis.rtp.total_rtp > 0


def test_build_calibration_report_wrapper() -> None:
    payload = load_golden_fixture_json("fixture-02-base-free-spins", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    report = build_calibration_report(
        game,
        simulated_rtp=0.5,
        simulated_feature_frequencies={"FREE_SPINS": 0.1},
        rtp_variance=0.03,
    )
    assert report["calibration"]["theoreticalRtp"] > 0
    assert report["recommendations"]


def test_discrepancy_summary_paths() -> None:
    theoretical = TheoreticalRtpResult(
        totalRtp=0.05,
        baseRtp=0.05,
        scatterRtp=0.0,
        lineRtp=0.05,
        outcomeCount=100,
        reelSetId="base_game",
    )
    calibration = calibrate_rtp(
        theoretical_rtp=theoretical,
        simulated_rtp=0.5,
        target_rtp=96.0,
        tolerance=0.1,
    )
    analysis = analyze_discrepancies(
        calibration,
        feature_probabilities=calculate_feature_probabilities(
            GameVersion.model_validate(
                load_golden_fixture_json("fixture-02-base-free-spins", repo_root=_repo_root()),
            ),
        ),
        simulated_feature_frequencies={"FREE_SPINS": 0.9},
        rtp_variance=0.01,
    )
    assert analysis.summary
    assert any(item.status == "critical" for item in analysis.items)


def test_recommendations_when_below_target() -> None:
    payload = load_golden_fixture_json("fixture-02-base-free-spins", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    theoretical = calculate_theoretical_rtp(game)
    features = calculate_feature_probabilities(game)
    calibration = calibrate_rtp(
        theoretical_rtp=theoretical,
        target_rtp=96.0,
        tolerance=0.1,
    )
    recommendations = generate_calibration_recommendations(
        game,
        calibration,
        theoretical,
        features,
    )
    assert recommendations
    assert any("Increase" in rec.action for rec in recommendations)


def test_recommendations_simulation_gap() -> None:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    theoretical = calculate_theoretical_rtp(game)
    calibration = calibrate_rtp(
        theoretical_rtp=theoretical,
        simulated_rtp=0.20,
        target_rtp=96.0,
        tolerance=0.1,
    )
    recommendations = generate_calibration_recommendations(
        game,
        calibration,
        theoretical,
        calculate_feature_probabilities(game),
    )
    assert any(rec.category == "simulation_validation" for rec in recommendations)


def test_weighted_reel_strips() -> None:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    payload["reelSets"]["base_game"]["reels"][0]["weights"] = [1, 1, 1, 1, 10]
    game = GameVersion.model_validate(payload)
    result = calculate_theoretical_rtp(game)
    assert result.total_rtp >= 0


def test_invalid_reel_set_raises() -> None:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    with pytest.raises(ValueError, match="reel set"):
        calculate_theoretical_rtp(game, reel_set_id="missing")


def test_unsupported_win_model_raises() -> None:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    payload["winModel"]["type"] = "ways"
    game = GameVersion.model_validate(payload)
    with pytest.raises(ValueError, match="unsupported win model"):
        calculate_theoretical_rtp(game)


def test_export_helpers_from_report_module() -> None:
    payload = load_golden_fixture_json("fixture-03-base-hold-win", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    report_payload = build_calibration_report(game, simulated_rtp=0.1)
    from runtime_core.theoretical.certification import build_certification_report

    report = build_certification_report(game, simulated_rtp=0.1)
    assert export_certification_json(report)
    pdf = export_certification_pdf(report)
    assert b"Exposure" in pdf
    assert report_payload["engineVersion"]


def test_lower_rtp_recommendations_with_features() -> None:
    payload = load_golden_fixture_json("fixture-02-base-free-spins", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    theoretical = calculate_theoretical_rtp(game)
    features = calculate_feature_probabilities(game)
    calibration = calibrate_rtp(
        theoretical_rtp=theoretical,
        target_rtp=1.0,
        tolerance=0.1,
    )
    recommendations = generate_calibration_recommendations(
        game,
        calibration,
        theoretical,
        features,
    )
    assert any("scatter frequency" in rec.action for rec in recommendations)


def test_jackpot_lower_recommendation() -> None:
    payload = load_golden_fixture_json("fixture-03-base-hold-win", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    theoretical = calculate_theoretical_rtp(game)
    calibration = calibrate_rtp(
        theoretical_rtp=theoretical,
        target_rtp=1.0,
        tolerance=0.1,
    )
    recommendations = generate_calibration_recommendations(
        game,
        calibration,
        theoretical,
        calculate_feature_probabilities(game),
    )
    assert any("GRAND" in rec.action for rec in recommendations)


def test_discrepancy_within_tolerance_summary() -> None:
    theoretical = TheoreticalRtpResult(
        totalRtp=0.96,
        baseRtp=0.96,
        scatterRtp=0.0,
        lineRtp=0.96,
        outcomeCount=100,
        reelSetId="base_game",
    )
    calibration = calibrate_rtp(
        theoretical_rtp=theoretical,
        simulated_rtp=0.96,
        target_rtp=96.0,
        tolerance=1.0,
    )
    analysis = analyze_discrepancies(calibration)
    assert "within configured tolerance" in analysis.summary


def test_substitute_all_paying_wild() -> None:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    payload["symbols"]["WILD"] = {
        "id": "WILD",
        "type": "wild",
        "substituteAllPaying": True,
    }
    game = GameVersion.model_validate(payload)
    result = calculate_theoretical_rtp(game)
    assert result.total_rtp >= 0


def test_non_positive_strip_weights_raise() -> None:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    payload["reelSets"]["base_game"]["reels"][0]["weights"] = [0, 0, 0, 0, 0]
    game = GameVersion.model_validate(payload)
    with pytest.raises(ValueError, match="non-positive weight"):
        calculate_theoretical_rtp(game)


def test_feature_probability_deduplication() -> None:
    payload = load_golden_fixture_json("fixture-04-nested-fs-hold-win", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    probabilities = calculate_feature_probabilities(game)
    triggers = [item.trigger for item in probabilities]
    assert len(triggers) == len(set(triggers))


def test_reel_count_mismatch_raises() -> None:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    payload["reelSets"]["base_game"]["reels"] = payload["reelSets"]["base_game"]["reels"][:3]
    game = GameVersion.model_validate(payload)
    with pytest.raises(ValueError, match="has 3 reels"):
        calculate_theoretical_rtp(game)


def test_empty_reel_strip_raises() -> None:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    payload["reelSets"]["base_game"]["reels"][0]["symbols"] = []
    game = GameVersion.model_validate(payload)
    with pytest.raises(ValueError, match="is empty"):
        calculate_theoretical_rtp(game)


def test_discrepancy_warning_and_divergence_summaries() -> None:
    theoretical = TheoreticalRtpResult(
        totalRtp=0.5015,
        baseRtp=0.5015,
        scatterRtp=0.0,
        lineRtp=0.5015,
        outcomeCount=100,
        reelSetId="base_game",
    )
    calibration = calibrate_rtp(
        theoretical_rtp=theoretical,
        simulated_rtp=0.5015,
        target_rtp=50.0,
        tolerance=0.1,
    )
    warning_analysis = analyze_discrepancies(calibration)
    assert "outside tolerance" in warning_analysis.summary

    no_target = calibrate_rtp(theoretical_rtp=theoretical)
    assert analyze_discrepancies(no_target).summary == "Discrepancy analysis complete."

    divergent_analysis = analyze_discrepancies(
        CalibrationResult(
            targetRtp=None,
            theoreticalRtp=50.15,
            simulatedRtp=None,
            targetDelta=None,
            theoryVsSimulationDelta=None,
            withinTolerance=False,
            tolerance=0.01,
        ),
    )
    assert "diverge from target" in divergent_analysis.summary


def test_free_spin_award_recommendation() -> None:
    payload = load_golden_fixture_json("fixture-02-base-free-spins", repo_root=_repo_root())
    payload["stateMachines"]["main"]["states"]["BASE"]["pluginConfig"]["scatterTriggers"][0][
        "awardSpins"
    ] = 15
    game = GameVersion.model_validate(payload)
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
    assert any("Free Spins awards" in rec.action for rec in recommendations)


def test_certification_document_id() -> None:
    from runtime_core.theoretical.certification import certification_report_document_id

    first = certification_report_document_id()
    second = certification_report_document_id()
    assert first
    assert first != second


def test_paytable_fallback_recommendation() -> None:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    theoretical = calculate_theoretical_rtp(game)
    calibration = calibrate_rtp(
        theoretical_rtp=theoretical,
        target_rtp=1.0,
        tolerance=0.1,
    )
    recommendations = generate_calibration_recommendations(
        game,
        calibration,
        theoretical,
        (),
    )
    assert any("Reduce" in rec.action for rec in recommendations)


def test_build_calibration_report_without_simulation() -> None:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    report = build_calibration_report(game)
    assert report["calibration"]["simulatedRtp"] is None


def test_custom_total_bet_override() -> None:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    default_result = calculate_theoretical_rtp(game)
    custom_result = calculate_theoretical_rtp(game, total_bet_minor_units=5000)
    assert default_result.total_rtp == pytest.approx(custom_result.total_rtp)


def test_jackpot_probability_with_positive_haw_trigger() -> None:
    payload = load_golden_fixture_json("fixture-03-base-hold-win", repo_root=_repo_root())
    payload["stateMachines"]["main"]["states"]["BASE"]["pluginConfig"]["bonusTriggers"][0][
        "minCount"
    ] = 5
    game = GameVersion.model_validate(payload)
    probabilities = calculate_feature_probabilities(game)
    grand = next(item for item in probabilities if item.trigger == "JACKPOT_GRAND")
    assert grand.probability > 0.0
    assert grand.one_in_x is not None
