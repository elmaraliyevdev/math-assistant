"""Apply plugin-requested frame counter and local-state mutations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from runtime_core.plugins.contracts import CounterUpdateRequest, FeatureStepResult
from runtime_core.runtime.events.payloads import FeatureCounterUpdatePayload
from runtime_core.runtime.frames import FrameContext

_COUNTER_ATTRS: dict[str, str] = {
    "spinsRemaining": "spins_remaining",
    "respinsRemaining": "respins_remaining",
}


@dataclass
class StepSideEffectResult:
    counter_events: list[FeatureCounterUpdatePayload] = field(default_factory=list)


def apply_frame_local_patch(
    frame_context: FrameContext,
    patch: dict[str, Any],
) -> None:
    if not patch:
        return
    frame_context.frame_local_state.update(patch)
    held = patch.get("heldSymbols")
    if isinstance(held, list):
        from runtime_core.runtime.frames import HeldSymbol

        frame_context.held_symbols = [
            HeldSymbol(
                reel=int(item["reel"]),
                row=int(item["row"]),
                symbol_id=str(item["symbolId"]),
            )
            for item in held
            if isinstance(item, dict)
        ]


def apply_counter_updates(
    frame_context: FrameContext,
    updates: list[CounterUpdateRequest],
) -> list[FeatureCounterUpdatePayload]:
    events: list[FeatureCounterUpdatePayload] = []
    for update in updates:
        attr = _COUNTER_ATTRS.get(update.field)
        if attr is None:
            msg = f"unsupported counter field {update.field!r}"
            raise ValueError(msg)
        before = int(getattr(frame_context, attr))
        setattr(frame_context, attr, update.after)
        events.append(
            FeatureCounterUpdatePayload(
                field=update.field,
                before=before,
                after=update.after,
            ),
        )
    return events


def apply_step_side_effects(
    frame_context: FrameContext,
    result: FeatureStepResult,
) -> StepSideEffectResult:
    apply_frame_local_patch(frame_context, result.frame_local_patch)
    counter_events = apply_counter_updates(frame_context, result.counter_updates)
    return StepSideEffectResult(counter_events=counter_events)
