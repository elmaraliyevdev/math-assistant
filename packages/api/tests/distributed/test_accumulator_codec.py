"""Accumulator codec tests."""

from __future__ import annotations

from runtime_core.simulation import PartialAccumulator

from app.distributed.accumulator_codec import (
    partial_accumulator_from_dict,
    partial_accumulator_to_dict,
)


def test_partial_accumulator_roundtrip() -> None:
    original = PartialAccumulator(
        spin_count=10,
        total_bet_minor_units=1000,
        total_win_minor_units=450,
        feature_trigger_counts={"FREE_SPINS": 2},
    )
    restored = partial_accumulator_from_dict(partial_accumulator_to_dict(original))
    assert restored.spin_count == original.spin_count
    assert restored.total_bet_minor_units == original.total_bet_minor_units
    assert restored.total_win_minor_units == original.total_win_minor_units
    assert restored.feature_trigger_counts == original.feature_trigger_counts
