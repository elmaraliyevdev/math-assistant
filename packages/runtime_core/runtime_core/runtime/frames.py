"""Per-stack-frame mutable state (Runtime Core §6.2, §15.3)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class HeldSymbol:
    reel: int
    row: int
    symbol_id: str


@dataclass
class FrameContext:
    spins_remaining: int = 0
    respins_remaining: int = 0
    held_symbols: list[HeldSymbol] = field(default_factory=list)
    active_multiplier: str = ""
    frame_local_state: dict[str, Any] = field(default_factory=dict)


def new_frame_context() -> FrameContext:
    return FrameContext(frame_local_state={})
