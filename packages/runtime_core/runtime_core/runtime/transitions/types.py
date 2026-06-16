"""Transition resolution result types."""

from __future__ import annotations

from dataclasses import dataclass

from runtime_core.domain.state_machine import Transition
from runtime_core.runtime.spin_chain import ChainFault


@dataclass(frozen=True, slots=True)
class TransitionResolution:
    """Successful two-phase resolution outcome."""

    selected_token: str
    transition: Transition
    warnings: tuple[ChainFault, ...] = ()


@dataclass(frozen=True, slots=True)
class TransitionResolveResult:
    """Outcome of transition resolution (§10.1)."""

    resolution: TransitionResolution | None = None
    fault: ChainFault | None = None
    continue_multistep: bool = False
