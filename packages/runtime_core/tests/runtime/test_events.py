"""Runtime event model and logger tests."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from runtime_core.runtime.events import EventContext, EventCorrelation, should_emit
from runtime_core.runtime.events.envelope import RuntimeEvent
from runtime_core.runtime.events.logger import EventLogger
from runtime_core.runtime.events.payloads import (
    PAYLOAD_MODEL_BY_EVENT_TYPE,
    SpinChainEndPayload,
    SpinChainStartPayload,
    TransitionTakenPayload,
    validate_payload,
)
from runtime_core.runtime.events.types import EVENT_VERSION, EventLogMode, EventType
from runtime_core.runtime.version import ENGINE_VERSION


def correlation() -> EventCorrelation:
    return EventCorrelation(
        simulation_run_id="run-1",
        spin_chain_index=7,
        game_version_content_hash="abc123",
        engine_version=ENGINE_VERSION,
    )


def context() -> EventContext:
    return EventContext(
        stack_depth=0,
        machine_id="main",
        state_id="BASE",
        frame_id="f-0-0",
    )


def spin_start_payload() -> dict[str, object]:
    return {"masterSeed": "00", "betMinorUnits": 100}


@pytest.mark.parametrize(
    ("mode", "event_type", "expected"),
    [
        (EventLogMode.NONE, EventType.SPIN_CHAIN_START, False),
        (EventLogMode.TRANSITIONS_ONLY, EventType.SPIN_CHAIN_START, True),
        (EventLogMode.TRANSITIONS_ONLY, EventType.WIN_EVALUATED, False),
        (EventLogMode.TRANSITIONS_ONLY, EventType.STATE_REENTER, False),
        (EventLogMode.FULL, EventType.WIN_EVALUATED, True),
        (EventLogMode.FULL, EventType.RNG_DRAW, False),
        (EventLogMode.REPLAY, EventType.RNG_DRAW, True),
        (EventLogMode.REPLAY, EventType.GUARD_EVALUATED, True),
    ],
)
def test_should_emit_modes(
    mode: EventLogMode,
    event_type: EventType,
    expected: bool,
) -> None:
    assert should_emit(mode, event_type) is expected


def test_should_emit_unknown_mode() -> None:
    assert should_emit("unknown", EventType.SPIN_CHAIN_START) is False  # type: ignore[arg-type]


def test_logger_append_sequence_and_correlation() -> None:
    logger = EventLogger(EventLogMode.FULL, correlation(), context())
    logger.append(EventType.SPIN_CHAIN_START, spin_start_payload())
    logger.append(
        EventType.SPIN_CHAIN_END,
        {"totalWinMinorUnits": 0, "stepCount": 0},
    )
    events = logger.events
    assert len(events) == 2
    assert events[0].sequence == 0
    assert events[1].sequence == 1
    assert events[0].event_version == EVENT_VERSION
    assert events[0].correlation.simulation_run_id == "run-1"


def test_logger_filters_by_mode() -> None:
    logger = EventLogger(EventLogMode.TRANSITIONS_ONLY, correlation(), context())
    logger.append(
        EventType.WIN_EVALUATED,
        {
            "rtpCategory": "BASE",
            "components": [],
            "totalWinMinorUnits": 0,
        },
    )
    logger.append(
        EventType.TRANSITION_TAKEN,
        {
            "transitionId": "t1",
            "trigger": "SPIN_COMPLETE",
            "effect": "stay",
            "priority": 1000,
            "priorityTier": "FALLBACK",
        },
    )
    assert len(logger.events) == 1
    assert logger.events[0].event_type == EventType.TRANSITION_TAKEN


def test_logger_hash_stable_without_timestamp() -> None:
    logger_a = EventLogger(EventLogMode.FULL, correlation(), context())
    logger_a.emit(
        EventType.SPIN_CHAIN_START,
        spin_start_payload(),
        timestamp_us=111,
    )
    hash_a = logger_a.replay_hash

    logger_b = EventLogger(EventLogMode.FULL, correlation(), context())
    logger_b.emit(
        EventType.SPIN_CHAIN_START,
        spin_start_payload(),
        timestamp_us=999,
    )
    hash_b = logger_b.replay_hash
    assert hash_a == hash_b


def test_logger_hash_empty() -> None:
    logger = EventLogger(EventLogMode.FULL, correlation(), context())
    assert logger.replay_hash == ""


def test_replay_unit_omits_timestamp() -> None:
    event = RuntimeEvent(
        sequence=3,
        event_type=EventType.GRID_RESULT,
        timestamp_us=42,
        correlation=correlation(),
        context=context(),
        payload={"reelSetId": "base", "symbols": [["H1"]], "rngDrawIds": [1]},
    )
    unit = event.replay_unit()
    assert "timestampUs" not in unit
    assert unit["sequence"] == 3
    assert unit["eventType"] == "GRID_RESULT"


def test_transition_mode_includes_frame_pop() -> None:
    assert should_emit(EventLogMode.TRANSITIONS_ONLY, EventType.FRAME_POP) is True


def test_full_mode_includes_runtime_fault() -> None:
    assert should_emit(EventLogMode.FULL, EventType.RUNTIME_FAULT) is True


def test_full_mode_excludes_rng_draw() -> None:
    assert should_emit(EventLogMode.FULL, EventType.RNG_DRAW) is False


def test_all_mvp_payload_models_registered() -> None:
    for event_type in EventType:
        assert event_type.value in PAYLOAD_MODEL_BY_EVENT_TYPE


def test_validate_payload_unknown_type() -> None:
    with pytest.raises(ValueError, match="unknown event type"):
        validate_payload("NOT_AN_EVENT", {})


def test_payload_models_frozen() -> None:
    payload = SpinChainStartPayload.model_validate(
        {"masterSeed": "ab", "betMinorUnits": 1},
    )
    with pytest.raises(ValidationError, match="frozen"):
        payload.master_seed = "cd"  # type: ignore[misc]


def test_spin_chain_payload_aliases() -> None:
    raw = validate_payload(
        "SPIN_CHAIN_START",
        {"masterSeed": "seed", "betMinorUnits": 500},
    )
    assert raw == {"masterSeed": "seed", "betMinorUnits": 500}


def test_transition_taken_payload_optional_fields() -> None:
    payload = TransitionTakenPayload.model_validate(
        {
            "transitionId": "t1",
            "trigger": "SPIN_COMPLETE",
            "effect": "stay",
            "priority": 1,
            "priorityTier": "FALLBACK",
        },
    )
    dumped = payload.model_dump(by_alias=True, exclude_none=True)
    assert "targetMachineId" not in dumped


def test_canonical_event_line_excludes_timestamp() -> None:
    event = RuntimeEvent(
        sequence=0,
        event_type=EventType.SPIN_CHAIN_START,
        timestamp_us=123,
        correlation=correlation(),
        context=context(),
        payload=validate_payload("SPIN_CHAIN_START", spin_start_payload()),
    )
    line = json.dumps(event.replay_unit(), sort_keys=True, separators=(",", ":"))
    decoded = json.loads(line)
    assert "timestampUs" not in decoded


def test_spin_chain_end_payload() -> None:
    payload = SpinChainEndPayload(total_win_minor_units=100, step_count=3)
    assert payload.step_count == 3


def test_logger_set_context_and_sequence() -> None:
    logger = EventLogger(EventLogMode.FULL, correlation(), context())
    assert logger.sequence == 0
    logger.set_context(
        EventContext(stack_depth=1, machine_id="m", state_id="s", frame_id="f"),
    )
    logger.append(EventType.SPIN_CHAIN_START, spin_start_payload())
    assert logger.sequence == 1


def test_emit_returns_none_when_filtered() -> None:
    logger = EventLogger(EventLogMode.NONE, correlation(), context())
    assert logger.emit(EventType.SPIN_CHAIN_START, spin_start_payload()) is None


def test_logger_append_alias() -> None:
    logger = EventLogger(EventLogMode.FULL, correlation(), context())
    event = logger.append(EventType.SPIN_CHAIN_START, spin_start_payload())
    assert event is not None
    assert event.event_type == EventType.SPIN_CHAIN_START
