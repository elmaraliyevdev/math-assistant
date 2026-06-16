"""Lifecycle effect handling tests."""

from __future__ import annotations

import pytest

from runtime_core.domain.game_version import GameVersion
from runtime_core.runtime.exceptions import RuntimeError
from runtime_core.runtime.lifecycle import apply_transition
from runtime_core.runtime.stack import ExecutionStack
from runtime_core.runtime.transitions import resolve_transition
from runtime_core.validation.validators.priority_tiers import PriorityTierRegistry


def test_stay_keeps_state(
    base_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(base_game)
    resolved = resolve_transition(base_game, frame, ["SPIN_COMPLETE"], priority_tiers)
    assert resolved.resolution is not None
    outcome = apply_transition(
        stack,
        base_game,
        frame,
        resolved.resolution.transition,
    )
    assert outcome.effect == "stay"
    assert outcome.state_changed is False
    assert stack.top() is not None
    assert stack.top().state_id == "BASE"


def test_goto_changes_state(
    nested_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(nested_game)
    resolved = resolve_transition(nested_game, frame, ["FREE_SPINS"], priority_tiers)
    assert resolved.resolution is not None
    outcome = apply_transition(
        stack,
        nested_game,
        frame,
        resolved.resolution.transition,
    )
    assert outcome.effect == "goto"
    assert outcome.state_changed is True
    assert stack.top() is not None
    assert stack.top().state_id == "FREE_SPINS"
    assert stack.top().plugin_ref_id == "fs_main"


def test_goto_self_normalized_to_stay(
    base_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(base_game)
    transition = base_game.state_machines["main"].states["BASE"].transitions[0].model_copy(
        update={"effect": "goto", "target_state_id": "BASE"},
    )
    outcome = apply_transition(stack, base_game, frame, transition)
    assert outcome.effect == "stay"
    assert any(w.code == "GOTO_SELF_NORMALIZED" for w in outcome.warnings)


def test_spawn_pushes_child_and_freezes_parent(
    nested_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(nested_game)
    resolved = resolve_transition(
        nested_game,
        frame,
        ["HOLD_AND_WIN"],
        priority_tiers,
    )
    assert resolved.resolution is not None
    outcome = apply_transition(
        stack,
        nested_game,
        frame,
        resolved.resolution.transition,
    )
    assert outcome.effect == "spawn"
    assert outcome.pushed_frame is not None
    assert stack.depth == 2
    assert stack.parent() is not None
    assert stack.parent().frozen is True
    assert stack.top() is not None
    assert stack.top().state_id == "HAW_RESPINS"


def test_pop_resumes_parent(
    nested_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=4)
    root = stack.push_root(nested_game)
    root.frame_context.spins_remaining = 5
    haw = stack.push_child(nested_game, "hold_and_win")
    transition = nested_game.state_machines["hold_and_win"].states[
        "HAW_RESPINS"
    ].transitions[0]
    outcome = apply_transition(stack, nested_game, haw, transition)
    assert outcome.effect == "pop"
    assert outcome.popped_frame is not None
    assert stack.depth == 1
    assert root.frozen is False
    assert root.frame_context.spins_remaining == 5


def test_invalid_pop_at_root(
    base_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(base_game)
    transition = base_game.state_machines["main"].states["BASE"].transitions[0].model_copy(
        update={"effect": "pop", "trigger": "FEATURE_COMPLETE"},
    )
    outcome = apply_transition(stack, base_game, frame, transition)
    assert outcome.fault is not None
    assert outcome.fault.code == "INVALID_POP"


def test_spawn_at_max_depth_returns_fault(nested_game: GameVersion) -> None:
    stack = ExecutionStack(max_depth=2)
    frame = stack.push_root(nested_game)
    stack.push_child(nested_game, "hold_and_win")
    transition = nested_game.state_machines["main"].states["BASE"].transitions[1]
    outcome = apply_transition(stack, nested_game, frame, transition)
    assert outcome.fault is not None
    assert outcome.fault.code == "MAX_STACK_DEPTH"


def test_unsupported_effect_raises(base_game: GameVersion) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(base_game)
    transition = base_game.state_machines["main"].states["BASE"].transitions[0].model_copy(
        update={"effect": "teleport"},
    )
    with pytest.raises(RuntimeError, match="unsupported transition effect"):
        apply_transition(stack, base_game, frame, transition)


def test_stay_with_mismatched_target_raises(base_game: GameVersion) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(base_game)
    transition = base_game.state_machines["main"].states["BASE"].transitions[0].model_copy(
        update={"target_state_id": "FREE_SPINS"},
    )
    with pytest.raises(RuntimeError, match="stay transition"):
        apply_transition(stack, base_game, frame, transition)


def test_goto_missing_target_raises(base_game: GameVersion) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(base_game)
    transition = base_game.state_machines["main"].states["BASE"].transitions[0].model_copy(
        update={"effect": "goto", "target_state_id": None},
    )
    with pytest.raises(RuntimeError, match="missing targetStateId"):
        apply_transition(stack, base_game, frame, transition)


def test_goto_unknown_state_raises(base_game: GameVersion) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(base_game)
    transition = base_game.state_machines["main"].states["BASE"].transitions[0].model_copy(
        update={"effect": "goto", "target_state_id": "NOPE"},
    )
    with pytest.raises(RuntimeError, match="goto target state"):
        apply_transition(stack, base_game, frame, transition)


def test_spawn_missing_target_machine_raises(base_game: GameVersion) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(base_game)
    transition = base_game.state_machines["main"].states["BASE"].transitions[0].model_copy(
        update={"effect": "spawn", "target_machine_id": None},
    )
    with pytest.raises(RuntimeError, match="missing targetMachineId"):
        apply_transition(stack, base_game, frame, transition)
