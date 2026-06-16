"""Transition effect lifecycle handling (§10.2, §10.6)."""

from __future__ import annotations

from dataclasses import dataclass

from runtime_core.domain.game_version import GameVersion
from runtime_core.domain.state_machine import Transition
from runtime_core.runtime.exceptions import RuntimeError
from runtime_core.runtime.spin_chain import ChainFault
from runtime_core.runtime.stack.execution_stack import ExecutionStack, StackLimitError
from runtime_core.runtime.stack.frame import StateMachineFrame, build_frame


@dataclass(frozen=True, slots=True)
class LifecycleOutcome:
    """Result of applying a transition effect to the stack."""

    effect: str
    frame: StateMachineFrame
    popped_frame: StateMachineFrame | None = None
    pushed_frame: StateMachineFrame | None = None
    state_changed: bool = False
    warnings: tuple[ChainFault, ...] = ()
    fault: ChainFault | None = None


def apply_transition(
    stack: ExecutionStack,
    game: GameVersion,
    frame: StateMachineFrame,
    transition: Transition,
    *,
    warnings: tuple[ChainFault, ...] = (),
) -> LifecycleOutcome:
    """Apply *transition* effect to *stack*; mutates stack and active frame."""
    effect = transition.effect
    if effect == "stay":
        return _apply_stay(frame, transition, warnings=warnings)
    if effect == "goto":
        return _apply_goto(stack, game, frame, transition, warnings=warnings)
    if effect == "spawn":
        return _apply_spawn(stack, game, frame, transition, warnings=warnings)
    if effect == "pop":
        return _apply_pop(stack, frame, transition, warnings=warnings)
    msg = f"unsupported transition effect {effect!r}"
    raise RuntimeError(msg)


def _apply_stay(
    frame: StateMachineFrame,
    transition: Transition,
    *,
    warnings: tuple[ChainFault, ...],
) -> LifecycleOutcome:
    target = transition.target_state_id or frame.state_id
    if target != frame.state_id:
        msg = (
            f"stay transition {transition.id!r} targets {target!r} "
            f"but current state is {frame.state_id!r}"
        )
        raise RuntimeError(msg)
    return LifecycleOutcome(effect="stay", frame=frame, warnings=warnings)


def _apply_goto(
    stack: ExecutionStack,
    game: GameVersion,
    frame: StateMachineFrame,
    transition: Transition,
    *,
    warnings: tuple[ChainFault, ...],
) -> LifecycleOutcome:
    target_id = transition.target_state_id
    if not target_id:
        msg = f"goto transition {transition.id!r} missing targetStateId"
        raise RuntimeError(msg)

    if target_id == frame.state_id:
        normalized = ChainFault(
            code="GOTO_SELF_NORMALIZED",
            message=(
                f"goto transition {transition.id!r} self-targets {target_id!r}; "
                "normalized to stay"
            ),
            frame_id=frame.frame_id,
        )
        return _apply_stay(frame, transition, warnings=warnings + (normalized,))

    machine = game.state_machines[frame.machine_id]
    target_state = machine.states.get(target_id)
    if target_state is None:
        msg = f"goto target state {target_id!r} not found"
        raise RuntimeError(msg)

    updated = build_frame(
        frame_id=frame.frame_id,
        machine_id=frame.machine_id,
        state=target_state,
        frame_context=frame.frame_context,
        frozen=frame.frozen,
    )
    _replace_top(stack, updated)
    return LifecycleOutcome(
        effect="goto",
        frame=updated,
        state_changed=True,
        warnings=warnings,
    )


def _apply_spawn(
    stack: ExecutionStack,
    game: GameVersion,
    frame: StateMachineFrame,
    transition: Transition,
    *,
    warnings: tuple[ChainFault, ...],
) -> LifecycleOutcome:
    target_machine_id = transition.target_machine_id
    if not target_machine_id:
        msg = f"spawn transition {transition.id!r} missing targetMachineId"
        raise RuntimeError(msg)
    try:
        child = stack.push_child(game, target_machine_id)
    except StackLimitError as exc:
        return LifecycleOutcome(
            effect="spawn",
            frame=frame,
            warnings=warnings,
            fault=ChainFault(
                code="MAX_STACK_DEPTH",
                message=str(exc),
                frame_id=frame.frame_id,
            ),
        )
    parent = stack.parent()
    assert parent is not None
    return LifecycleOutcome(
        effect="spawn",
        frame=child,
        pushed_frame=child,
        state_changed=True,
        warnings=warnings,
    )


def _apply_pop(
    stack: ExecutionStack,
    frame: StateMachineFrame,
    transition: Transition,
    *,
    warnings: tuple[ChainFault, ...],
) -> LifecycleOutcome:
    if stack.depth <= 1:
        return LifecycleOutcome(
            effect="pop",
            frame=frame,
            warnings=warnings,
            fault=ChainFault(
                code="INVALID_POP",
                message="pop at root frame is forbidden",
                frame_id=frame.frame_id,
            ),
        )
    popped = stack.pop()
    resumed = stack.top()
    assert resumed is not None
    return LifecycleOutcome(
        effect="pop",
        frame=resumed,
        popped_frame=popped,
        warnings=warnings,
    )


def _replace_top(stack: ExecutionStack, frame: StateMachineFrame) -> None:
    stack.replace_top(frame)
