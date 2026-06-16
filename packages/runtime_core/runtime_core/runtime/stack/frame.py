"""State machine stack frame value object."""

from __future__ import annotations

from dataclasses import dataclass

from runtime_core.domain.state_machine import State
from runtime_core.runtime.frames import FrameContext, new_frame_context


@dataclass
class StateMachineFrame:
    """One active state machine instance on the execution stack (§7.2)."""

    frame_id: str
    machine_id: str
    state_id: str
    plugin_ref_id: str
    rtp_category: str
    frame_context: FrameContext
    frozen: bool = False


def build_frame(
    *,
    frame_id: str,
    machine_id: str,
    state: State,
    frame_context: FrameContext | None = None,
    frozen: bool = False,
) -> StateMachineFrame:
    return StateMachineFrame(
        frame_id=frame_id,
        machine_id=machine_id,
        state_id=state.id,
        plugin_ref_id=state.plugin_ref_id,
        rtp_category=state.rtp_category,
        frame_context=frame_context or new_frame_context(),
        frozen=frozen,
    )
