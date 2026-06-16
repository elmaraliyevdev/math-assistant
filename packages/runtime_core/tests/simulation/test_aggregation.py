"""Aggregation edge-case tests."""

from __future__ import annotations

from runtime_core.runtime.events import EventType, RuntimeEvent
from runtime_core.runtime.events.envelope import EventContext, EventCorrelation
from runtime_core.runtime.chain_metrics import ChainMetrics
from runtime_core.runtime.spin_chain import AccumulatorDelta, SpinChainResult
from runtime_core.simulation.aggregator import PartialAccumulator


def _chain_result(**overrides) -> SpinChainResult:
    defaults = dict(
        total_win_minor_units=100,
        total_uncapped_win_minor_units=120,
        total_truncated_minor_units=20,
        total_bet_minor_units=50,
        step_count=1,
        frame_push_count=0,
        exposure_cap_applied=True,
        limit_hit=None,
        fault=None,
        events=(),
        event_log_hash="",
        accumulator_delta=AccumulatorDelta(
            capped_win_minor_units=100,
            uncapped_win_minor_units=120,
            exposure_truncation_count=1,
            exposure_truncated_minor_units=20,
            chain_fault_count=0,
        ),
        chain_metrics=ChainMetrics.empty(),
    )
    defaults.update(overrides)
    return SpinChainResult(**defaults)


def test_add_chain_extracts_feature_triggers_from_chain_metrics() -> None:
    metrics = ChainMetrics(
        feature_trigger_counts={"FREE_SPINS": 1},
        win_by_rtp_category_minor_units={"BASE": 100},
        jackpot_counts={},
        nested_feature_entries=0,
    )
    result = _chain_result(chain_metrics=metrics)
    acc = PartialAccumulator.empty().add_chain(result, events_sampled=False)
    assert acc.feature_trigger_counts["FREE_SPINS"] == 1
    assert "SPIN_COMPLETE" not in acc.feature_trigger_counts
    assert acc.win_by_rtp_category_minor_units["BASE"] == 100


def test_add_chain_extracts_feature_triggers_from_events_legacy() -> None:
    event = RuntimeEvent(
        sequence=0,
        event_type=EventType.TRIGGER_EMITTED,
        correlation=EventCorrelation(
            simulation_run_id="r",
            spin_chain_index=0,
            game_version_content_hash="h",
            engine_version="runtime-core@1.8.0",
        ),
        context=EventContext(
            stack_depth=1,
            machine_id="main",
            state_id="BASE",
            frame_id="f-0-0",
        ),
        payload={"tokens": ["FREE_SPINS", "SPIN_COMPLETE"]},
    )
    result = _chain_result(events=(event,))
    acc = PartialAccumulator.empty().add_chain(result, events_sampled=False)
    assert acc.feature_trigger_counts == {}


def test_add_chain_extracts_jackpot_wins_from_chain_metrics() -> None:
    metrics = ChainMetrics(
        feature_trigger_counts={},
        win_by_rtp_category_minor_units={"HOLD_AND_WIN": 5000},
        jackpot_counts={"MINI": 1},
        nested_feature_entries=1,
    )
    result = _chain_result(chain_metrics=metrics)
    acc = PartialAccumulator.empty().add_chain(result, events_sampled=False)
    assert acc.jackpot_counts["MINI"] == 1
    assert acc.nested_feature_entries == 1


def test_add_chain_extracts_jackpot_wins_from_events_legacy() -> None:
    event = RuntimeEvent(
        sequence=0,
        event_type=EventType.WIN_EVALUATED,
        correlation=EventCorrelation(
            simulation_run_id="r",
            spin_chain_index=0,
            game_version_content_hash="h",
            engine_version="runtime-core@1.8.0",
        ),
        context=EventContext(
            stack_depth=1,
            machine_id="haw",
            state_id="HAW_RESPINS",
            frame_id="f-1-0",
        ),
        payload={
            "rtpCategory": "HOLD_AND_WIN",
            "components": [
                {
                    "source": "jackpot",
                    "symbolId": "MINI",
                    "count": 10,
                    "winMinorUnits": 5000,
                },
            ],
            "totalWinMinorUnits": 5000,
        },
    )
    result = _chain_result(events=(event,))
    acc = PartialAccumulator.empty().add_chain(result, events_sampled=True)
    assert acc.jackpot_counts == {}
    assert acc.event_sample_count == 1


def test_add_chain_counts_fatal_fault() -> None:
    from runtime_core.runtime.spin_chain import ChainFault

    result = _chain_result(
        fault=ChainFault(code="PLUGIN_FAULT", message="boom"),
        accumulator_delta=AccumulatorDelta(chain_fault_count=0),
    )
    acc = PartialAccumulator.empty().add_chain(result, events_sampled=False)
    assert acc.chain_fault_count == 1


def test_add_chain_ignores_malformed_trigger_payload() -> None:
    event = RuntimeEvent(
        sequence=0,
        event_type=EventType.TRIGGER_EMITTED,
        correlation=EventCorrelation(
            simulation_run_id="r",
            spin_chain_index=0,
            game_version_content_hash="h",
            engine_version="runtime-core@1.8.0",
        ),
        context=EventContext(
            stack_depth=1,
            machine_id="main",
            state_id="BASE",
            frame_id="f-0-0",
        ),
        payload={"tokens": "not-a-list"},
    )
    result = _chain_result(events=(event,))
    acc = PartialAccumulator.empty().add_chain(result, events_sampled=False)
    assert acc.feature_trigger_counts == {}


def test_add_chain_ignores_malformed_jackpot_payload() -> None:
    event = RuntimeEvent(
        sequence=0,
        event_type=EventType.WIN_EVALUATED,
        correlation=EventCorrelation(
            simulation_run_id="r",
            spin_chain_index=0,
            game_version_content_hash="h",
            engine_version="runtime-core@1.8.0",
        ),
        context=EventContext(
            stack_depth=1,
            machine_id="haw",
            state_id="HAW_RESPINS",
            frame_id="f-1-0",
        ),
        payload={"components": "not-a-list"},
    )
    result = _chain_result(events=(event,))
    acc = PartialAccumulator.empty().add_chain(result, events_sampled=False)
    assert acc.jackpot_counts == {}
