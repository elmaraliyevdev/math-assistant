"""Deterministic runtime event logger."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from runtime_core.runtime.events.envelope import (
    EventContext,
    EventCorrelation,
    RuntimeEvent,
)
from runtime_core.runtime.events.filters import should_emit
from runtime_core.runtime.events.payloads import validate_payload
from runtime_core.runtime.events.types import EventLogMode, EventType


@dataclass
class EventLogger:
    """Monotonic event sequencer with SHA-256 replay hashing."""

    mode: EventLogMode
    correlation: EventCorrelation
    context: EventContext
    _sequence: int = field(default=0, init=False)
    _events: list[RuntimeEvent] = field(default_factory=list, init=False)
    _hasher: hashlib._Hash = field(default_factory=hashlib.sha256, init=False)

    @property
    def sequence(self) -> int:
        return self._sequence

    @property
    def events(self) -> tuple[RuntimeEvent, ...]:
        return tuple(self._events)

    @property
    def replay_hash(self) -> str:
        if not self._events:
            return ""
        return self._hasher.hexdigest()

    def set_context(self, context: EventContext) -> None:
        self.context = context

    def emit(
        self,
        event_type: EventType,
        payload: dict[str, Any],
        *,
        timestamp_us: int | None = None,
    ) -> RuntimeEvent | None:
        if not should_emit(self.mode, event_type):
            return None
        canonical_payload = validate_payload(event_type.value, payload)
        event = RuntimeEvent(
            sequence=self._sequence,
            event_type=event_type,
            timestamp_us=timestamp_us,
            correlation=self.correlation,
            context=self.context,
            payload=canonical_payload,
        )
        self._sequence += 1
        self._events.append(event)
        unit = event.replay_unit()
        line = json.dumps(unit, sort_keys=True, separators=(",", ":"))
        self._hasher.update(line.encode("utf-8"))
        self._hasher.update(b"\n")
        return event

    def append(
        self,
        event_type: EventType,
        payload: dict[str, Any],
        *,
        timestamp_us: int | None = None,
    ) -> RuntimeEvent | None:
        """Alias for :meth:`emit` matching Go ``Append`` naming."""
        return self.emit(event_type, payload, timestamp_us=timestamp_us)
