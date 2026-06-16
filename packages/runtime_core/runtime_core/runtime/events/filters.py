"""Event emission filters by log mode."""

from runtime_core.runtime.events.types import EventLogMode, EventType

_TRANSITIONS_ONLY: frozenset[EventType] = frozenset(
    {
        EventType.SPIN_CHAIN_START,
        EventType.SPIN_CHAIN_END,
        EventType.FRAME_PUSH,
        EventType.FRAME_POP,
        EventType.STATE_ENTER,
        EventType.TRANSITION_TAKEN,
    },
)

_FULL: frozenset[EventType] = frozenset(
    {
        EventType.SPIN_CHAIN_START,
        EventType.SPIN_CHAIN_END,
        EventType.FRAME_PUSH,
        EventType.FRAME_POP,
        EventType.STATE_ENTER,
        EventType.STATE_REENTER,
        EventType.GRID_RESULT,
        EventType.WIN_EVALUATED,
        EventType.TRIGGER_EMITTED,
        EventType.TRANSITION_TAKEN,
        EventType.MULTIPLIER_APPLIED,
        EventType.EXPOSURE_CAP_APPLIED,
        EventType.FEATURE_COUNTER_UPDATE,
        EventType.RUNTIME_LIMIT_HIT,
        EventType.RUNTIME_FAULT,
    },
)

_REPLAY: frozenset[EventType] = _FULL | frozenset(
    {EventType.RNG_DRAW, EventType.GUARD_EVALUATED},
)


def should_emit(mode: EventLogMode | str, event_type: EventType) -> bool:
    try:
        resolved = EventLogMode(mode)
    except ValueError:
        return False
    match resolved:
        case EventLogMode.NONE:
            return False
        case EventLogMode.TRANSITIONS_ONLY:
            return event_type in _TRANSITIONS_ONLY
        case EventLogMode.FULL:
            return event_type in _FULL
        case EventLogMode.REPLAY:
            return event_type in _REPLAY
