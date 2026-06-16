"""Frame context and spin chain DTO tests."""

from __future__ import annotations

from runtime_core.runtime.frames import HeldSymbol, new_frame_context
from runtime_core.runtime.spin_chain import (
    AccumulatorDelta,
    ChainFault,
    LimitHit,
    SpinChainResult,
)


def test_frame_context() -> None:
    fc = new_frame_context()
    assert fc.spins_remaining == 0
    assert fc.respins_remaining == 0
    assert fc.held_symbols == []
    assert fc.frame_local_state == {}

    fc.spins_remaining = 10
    fc.held_symbols.append(HeldSymbol(reel=1, row=2, symbol_id="BONUS"))
    assert fc.spins_remaining == 10
    assert len(fc.held_symbols) == 1
    assert fc.held_symbols[0].symbol_id == "BONUS"


def test_spin_chain_result_types() -> None:
    result = SpinChainResult(
        total_win_minor_units=100,
        total_uncapped_win_minor_units=120,
        total_truncated_minor_units=20,
        total_bet_minor_units=50,
        step_count=3,
        frame_push_count=1,
        exposure_cap_applied=True,
        limit_hit=LimitHit(code="MAX_STEPS", action="abort"),
        fault=ChainFault(code="FAULT", message="test"),
        events=(),
        event_log_hash="abc",
        accumulator_delta=AccumulatorDelta(capped_win_minor_units=100),
    )
    assert result.limit_hit is not None
    assert result.limit_hit.code == "MAX_STEPS"
    assert result.fault is not None
    assert result.accumulator_delta.capped_win_minor_units == 100
