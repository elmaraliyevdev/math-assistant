"""RTP calculator tests."""

from __future__ import annotations

from runtime_core.mathematical.rtp import calculate_rtp
from tests.mathematical.conftest import sample_simulation_result


def test_calculate_rtp_capped_and_uncapped() -> None:
    result = sample_simulation_result(
        total_bet=10_000,
        total_win=9_500,
        uncapped_win=10_000,
    )
    rtp = calculate_rtp(result)
    assert rtp.rtp == 0.95
    assert rtp.uncapped_rtp == 1.0
    assert rtp.total_bet_minor_units == 10_000
    assert rtp.total_win_minor_units == 9_500
    assert rtp.uncapped_win_minor_units == 10_000


def test_calculate_rtp_zero_bet() -> None:
    result = sample_simulation_result(total_bet=0, total_win=0, uncapped_win=0)
    rtp = calculate_rtp(result)
    assert rtp.rtp == 0.0
    assert rtp.uncapped_rtp == 0.0
