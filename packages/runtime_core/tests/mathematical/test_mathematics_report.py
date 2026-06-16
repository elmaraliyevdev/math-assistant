"""MathematicsReport assembly tests."""

from __future__ import annotations

import pytest

from runtime_core.mathematical.report import build_mathematics_report
from tests.mathematical.conftest import SAMPLE_SPIN_WINS, sample_simulation_result


def test_build_mathematics_report_deterministic() -> None:
    result = sample_simulation_result(spin_count=4, total_bet=4000)
    first = build_mathematics_report(result, spin_wins_minor_units=SAMPLE_SPIN_WINS)
    second = build_mathematics_report(result, spin_wins_minor_units=SAMPLE_SPIN_WINS)
    assert first.model_dump() == second.model_dump()


def test_build_mathematics_report_zero_spins() -> None:
    result = sample_simulation_result(spin_count=0, total_bet=0, total_win=0)
    report = build_mathematics_report(result)
    assert report.spin_count == 0
    assert report.rtp.rtp == 0.0


def test_build_mathematics_report_requires_spin_wins() -> None:
    result = sample_simulation_result(spin_count=4)
    with pytest.raises(ValueError, match="spin_wins_minor_units required"):
        build_mathematics_report(result)
