"""Discrepancy analysis and certification report tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from runtime_core.common.golden import load_golden_fixture_json
from runtime_core.domain.game_version import GameVersion
from runtime_core.theoretical.calibration import calibrate_rtp
from runtime_core.theoretical.certification import build_certification_report
from runtime_core.theoretical.discrepancy import analyze_discrepancies
from runtime_core.theoretical.report import export_certification_json, export_certification_pdf
from runtime_core.theoretical.theoretical_features import calculate_feature_probabilities
from runtime_core.theoretical.theoretical_rtp import calculate_theoretical_rtp


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def test_discrepancy_analysis_flags_simulation_gap() -> None:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    theoretical = calculate_theoretical_rtp(game)
    calibration = calibrate_rtp(
        theoretical_rtp=theoretical,
        simulated_rtp=0.10,
        target_rtp=96.0,
        tolerance=0.1,
    )
    features = calculate_feature_probabilities(game)
    analysis = analyze_discrepancies(
        calibration,
        feature_probabilities=features,
        simulated_feature_frequencies={"FREE_SPINS": 0.5},
        rtp_variance=0.02,
    )
    assert analysis.items
    assert "simulation_vs_theoretical_rtp" in {item.metric for item in analysis.items}


def test_certification_report_contains_required_sections() -> None:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    report = build_certification_report(game, simulated_rtp=0.0512, rtp_variance=0.001)
    assert report.target_rtp == 96.0
    assert report.theoretical_rtp.total_rtp > 0.0
    assert report.simulated_rtp == pytest.approx(5.12, abs=0.01)
    assert report.exposure.max_win_minor_units == game.exposure.max_win_minor_units
    assert report.discrepancy is not None


def test_certification_export_formats() -> None:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    report = build_certification_report(game)
    json_bytes = export_certification_json(report)
    pdf_bytes = export_certification_pdf(report)
    assert b"gameTitle" in json_bytes
    assert b"Certification Mathematics Report" in pdf_bytes
