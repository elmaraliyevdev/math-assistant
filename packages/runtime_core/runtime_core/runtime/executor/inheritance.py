"""Spawn context inheritance for nested features (mvp-v1)."""

from __future__ import annotations

from runtime_core.runtime.frames import FrameContext

_INHERITED_KEYS = (
    "entryHeldSymbols",
    "scatterCounts",
    "entryScatterCount",
)


def inherit_spawn_context(parent: FrameContext, child: FrameContext) -> None:
    """Copy entry trigger context from a frozen parent frame to a child frame."""
    for key in _INHERITED_KEYS:
        value = parent.frame_local_state.get(key)
        if value is not None:
            child.frame_local_state[key] = value
