"""Deterministic transition resolution."""

from runtime_core.runtime.transitions.resolver import resolve_transition
from runtime_core.runtime.transitions.types import (
    TransitionResolution,
    TransitionResolveResult,
)

__all__ = [
    "TransitionResolution",
    "TransitionResolveResult",
    "resolve_transition",
]
