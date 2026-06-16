"""Golden fixture graph scenario tests (graph definitions only)."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.runtime.lifecycle import apply_transition
from runtime_core.runtime.stack import ExecutionStack
from runtime_core.runtime.transitions import resolve_transition
from runtime_core.validation.validators.priority_tiers import PriorityTierRegistry


def _resolve_and_apply(
    game: GameVersion,
    stack: ExecutionStack,
    frame,
    tokens: list[str],
    tiers: PriorityTierRegistry,
):
    result = resolve_transition(game, frame, tokens, tiers)
    assert result.fault is None, result.fault
    assert result.resolution is not None
    return apply_transition(
        stack,
        game,
        frame,
        result.resolution.transition,
        warnings=result.resolution.warnings,
    )


def test_golden_base_only_stay_loop(
    base_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=base_game.session.max_stack_depth)
    frame = stack.push_root(base_game)
    outcome = _resolve_and_apply(
        base_game,
        stack,
        frame,
        ["SPIN_COMPLETE"],
        priority_tiers,
    )
    assert outcome.effect == "stay"
    assert stack.depth == 1
    assert stack.top() is not None
    assert stack.top().state_id == "BASE"


def test_golden_base_to_free_spins(
    nested_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=nested_game.session.max_stack_depth)
    frame = stack.push_root(nested_game)
    outcome = _resolve_and_apply(
        nested_game,
        stack,
        frame,
        ["FREE_SPINS"],
        priority_tiers,
    )
    assert outcome.effect == "goto"
    assert stack.top() is not None
    assert stack.top().state_id == "FREE_SPINS"
    assert stack.top().rtp_category == "FREE_SPINS"


def test_golden_base_free_spins_hold_and_win_nested(
    nested_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=nested_game.session.max_stack_depth)
    frame = stack.push_root(nested_game)

    goto_fs = _resolve_and_apply(
        nested_game,
        stack,
        frame,
        ["FREE_SPINS"],
        priority_tiers,
    )
    assert goto_fs.effect == "goto"
    fs_frame = stack.top()
    assert fs_frame is not None
    fs_frame.frame_context.spins_remaining = 10

    spawn_hw = _resolve_and_apply(
        nested_game,
        stack,
        fs_frame,
        ["HOLD_AND_WIN"],
        priority_tiers,
    )
    assert spawn_hw.effect == "spawn"
    assert stack.depth == 2
    parent = stack.parent()
    assert parent is not None
    assert parent.state_id == "FREE_SPINS"
    assert parent.frozen is True
    assert parent.frame_context.spins_remaining == 10

    haw_frame = stack.top()
    assert haw_frame is not None
    pop_hw = _resolve_and_apply(
        nested_game,
        stack,
        haw_frame,
        ["FEATURE_COMPLETE"],
        priority_tiers,
    )
    assert pop_hw.effect == "pop"
    assert stack.depth == 1
    resumed = stack.top()
    assert resumed is not None
    assert resumed.state_id == "FREE_SPINS"
    assert resumed.frozen is False
    assert resumed.frame_context.spins_remaining == 10

    exit_fs = _resolve_and_apply(
        nested_game,
        stack,
        resumed,
        ["FEATURE_COMPLETE"],
        priority_tiers,
    )
    assert exit_fs.effect == "goto"
    assert stack.top() is not None
    assert stack.top().state_id == "BASE"
