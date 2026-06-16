"""RTP decomposition tests."""

from __future__ import annotations

from runtime_core.mathematical.rtp_decomposition import calculate_rtp_decomposition
from tests.mathematical.conftest import sample_simulation_result


def test_calculate_rtp_decomposition_by_category() -> None:
    result = sample_simulation_result(
        spin_count=100,
        total_bet=200_000,
        total_win=192_000,
        feature_triggers={"FREE_SPINS": 10},
    ).model_copy(
        update={
            "win_by_rtp_category_minor_units": {
                "BASE": 50_000,
                "FREE_SPINS": 100_000,
                "HOLD_AND_WIN": 42_000,
            },
        },
    )
    decomposition = calculate_rtp_decomposition(result)
    assert decomposition.total_rtp == 0.96
    shares = {item.rtp_category: item.rtp_share for item in decomposition.categories}
    assert shares["BASE"] == 0.25
    assert shares["FREE_SPINS"] == 0.5
    assert shares["HOLD_AND_WIN"] == 0.21
