"""Two-phase transition resolution (RUNTIME_CORE_DESIGN §10)."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.domain.state_machine import State, Transition
from runtime_core.runtime.spin_chain import ChainFault
from runtime_core.runtime.stack.frame import StateMachineFrame
from runtime_core.runtime.transitions.types import (
    TransitionResolution,
    TransitionResolveResult,
)
from runtime_core.validation.validators.priority_tiers import PriorityTierRegistry

_MISSING_TIER_SORT = 999_999


def resolve_transition(
    game: GameVersion,
    frame: StateMachineFrame,
    tokens: list[str],
    tiers: PriorityTierRegistry,
    *,
    step_complete: bool = True,
) -> TransitionResolveResult:
    """Resolve trigger tokens to a single transition for *frame*."""
    machine = game.state_machines.get(frame.machine_id)
    if machine is None:
        return TransitionResolveResult(
            fault=ChainFault(
                code="NO_MATCHING_TRANSITION",
                message=f"unknown machine {frame.machine_id!r}",
                frame_id=frame.frame_id,
            ),
        )
    state = machine.states.get(frame.state_id)
    if state is None:
        return TransitionResolveResult(
            fault=ChainFault(
                code="NO_MATCHING_TRANSITION",
                message=f"unknown state {frame.state_id!r}",
                frame_id=frame.frame_id,
            ),
        )

    token, token_fault = _select_token(game, tokens, step_complete=step_complete)
    if token_fault is not None:
        return TransitionResolveResult(fault=token_fault)
    if token is None:
        return TransitionResolveResult(continue_multistep=True)

    transition, transition_fault, warnings = _select_transition(
        state,
        token,
        tiers,
        frame_id=frame.frame_id,
    )
    if transition_fault is not None:
        return TransitionResolveResult(fault=transition_fault)
    assert transition is not None
    return TransitionResolveResult(
        resolution=TransitionResolution(
            selected_token=token,
            transition=transition,
            warnings=warnings,
        ),
    )


def _select_token(
    game: GameVersion,
    tokens: list[str],
    *,
    step_complete: bool,
) -> tuple[str | None, ChainFault | None]:
    if not tokens:
        if step_complete:
            return "SPIN_COMPLETE", None
        return None, None

    if len(tokens) == 1:
        return tokens[0], None

    order = game.precedence.trigger_order
    indices: dict[str, int] = {}
    for token in tokens:
        try:
            indices[token] = order.index(token)
        except ValueError:
            return None, ChainFault(
                code="AMBIGUOUS_TRIGGER",
                message=f"token {token!r} missing from precedence.triggerOrder",
            )

    min_index = min(indices.values())
    winners = sorted(token for token, idx in indices.items() if idx == min_index)
    if len(winners) > 1:
        return None, ChainFault(
            code="AMBIGUOUS_TRIGGER",
            message=f"tokens tied on triggerOrder index {min_index}: {winners}",
        )
    return winners[0], None


def _select_transition(
    state: State,
    token: str,
    tiers: PriorityTierRegistry,
    *,
    frame_id: str,
) -> tuple[Transition | None, ChainFault | None, tuple[ChainFault, ...]]:
    candidates = [t for t in state.transitions if t.trigger == token]
    if not candidates:
        return None, ChainFault(
            code="NO_MATCHING_TRANSITION",
            message=f"no transition for trigger {token!r} in state {state.id!r}",
            frame_id=frame_id,
        ), ()

    ranked = sorted(candidates, key=lambda t: _sort_key(t, tiers))
    if _has_ambiguous_rank(ranked, tiers):
        return None, ChainFault(
            code="AMBIGUOUS_TRANSITION",
            message=(
                f"multiple transitions rank equally for trigger {token!r} "
                f"in state {state.id!r}"
            ),
            frame_id=frame_id,
        ), ()

    return ranked[0], None, ()


def _sort_key(
    transition: Transition,
    tiers: PriorityTierRegistry,
) -> tuple[int, int, str]:
    tier = tiers.resolve(transition.priority_tier or "")
    tier_default = tier.default_priority if tier is not None else _MISSING_TIER_SORT
    return (transition.priority, tier_default, transition.id)


def _has_ambiguous_rank(
    ranked: list[Transition],
    tiers: PriorityTierRegistry,
) -> bool:
    if len(ranked) < 2:
        return False
    first_key = _sort_key(ranked[0], tiers)
    second_key = _sort_key(ranked[1], tiers)
    return first_key == second_key
