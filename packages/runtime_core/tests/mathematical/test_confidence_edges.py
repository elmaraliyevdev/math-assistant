"""Confidence interval edge coverage."""

from __future__ import annotations

import pytest

from runtime_core.mathematical.confidence import calculate_rtp_confidence_interval
from tests.mathematical.conftest import sample_simulation_result


def test_confidence_length_mismatch() -> None:
    result = sample_simulation_result(spin_count=2, total_bet=2000)
    with pytest.raises(ValueError, match="spin_wins length"):
        calculate_rtp_confidence_interval(result, (100,))
