"""Execution stack tests."""

from __future__ import annotations

import pytest

from runtime_core.domain.game_version import GameVersion
from runtime_core.runtime.exceptions import RuntimeError
from runtime_core.runtime.frames import new_frame_context
from runtime_core.runtime.stack import ExecutionStack, StackLimitError


def test_push_root_creates_deterministic_frame_id(base_game: GameVersion) -> None:
    stack = ExecutionStack(max_depth=base_game.session.max_stack_depth)
    frame = stack.push_root(base_game)
    assert frame.frame_id == "f-0-0"
    assert frame.machine_id == "main"
    assert frame.state_id == "BASE"
    assert frame.frozen is False
    assert stack.depth == 1


def test_push_root_requires_empty_stack(base_game: GameVersion) -> None:
    stack = ExecutionStack(max_depth=4)
    stack.push_root(base_game)
    with pytest.raises(RuntimeError, match="push_root requires empty stack"):
        stack.push_root(base_game)


def test_push_child_freezes_parent_and_assigns_frame_id(nested_game: GameVersion) -> None:
    stack = ExecutionStack(max_depth=nested_game.session.max_stack_depth)
    root = stack.push_root(nested_game)
    child = stack.push_child(nested_game, "hold_and_win")
    assert child.frame_id == "f-1-1"
    assert child.machine_id == "hold_and_win"
    assert child.state_id == "HAW_RESPINS"
    assert root.frozen is True
    assert child.frozen is False
    assert stack.depth == 2


def test_pop_resumes_parent(nested_game: GameVersion) -> None:
    stack = ExecutionStack(max_depth=4)
    root = stack.push_root(nested_game)
    root.frame_context.spins_remaining = 7
    stack.push_child(nested_game, "hold_and_win")
    popped = stack.pop()
    assert popped.state_id == "HAW_RESPINS"
    assert root.frozen is False
    assert root.frame_context.spins_remaining == 7
    assert stack.top() is root


def test_pop_at_root_forbidden(base_game: GameVersion) -> None:
    stack = ExecutionStack(max_depth=4)
    stack.push_root(base_game)
    with pytest.raises(RuntimeError, match="pop requires stack depth"):
        stack.pop()


def test_push_child_requires_parent(base_game: GameVersion) -> None:
    stack = ExecutionStack(max_depth=4)
    with pytest.raises(RuntimeError, match="push_child requires active parent"):
        stack.push_child(base_game, "hold_and_win")


def test_max_stack_depth_enforced(nested_game: GameVersion) -> None:
    stack = ExecutionStack(max_depth=2)
    stack.push_root(nested_game)
    stack.push_child(nested_game, "hold_and_win")
    with pytest.raises(StackLimitError):
        stack.push_child(nested_game, "hold_and_win")


def test_freeze_and_resume_explicitly(nested_game: GameVersion) -> None:
    stack = ExecutionStack(max_depth=4)
    root = stack.push_root(nested_game)
    stack.freeze_top()
    assert root.frozen is True
    stack.resume_parent()
    assert root.frozen is False


def test_replace_top(nested_game: GameVersion) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(nested_game)
    fs_state = nested_game.state_machines["main"].states["FREE_SPINS"]
    from runtime_core.runtime.stack import build_frame

    updated = build_frame(
        frame_id=frame.frame_id,
        machine_id=frame.machine_id,
        state=fs_state,
        frame_context=frame.frame_context,
    )
    stack.replace_top(updated)
    assert stack.top() is not None
    assert stack.top().state_id == "FREE_SPINS"


def test_stack_top_and_parent_empty() -> None:
    stack = ExecutionStack(max_depth=4)
    assert stack.top() is None
    assert stack.parent() is None


def test_replace_top_empty_stack_raises() -> None:
    stack = ExecutionStack(max_depth=4)
    from runtime_core.runtime.stack import build_frame

    frame = build_frame(
        frame_id="f-0-0",
        machine_id="main",
        state=__import__(
            "runtime_core.domain.state_machine",
            fromlist=["State"],
        ).State(
            id="BASE",
            plugin_ref_id="p",
            state_type="atomic_spin",
            rtp_category="BASE",
        ),
    )
    with pytest.raises(RuntimeError, match="cannot replace top frame"):
        stack.replace_top(frame)


def test_push_root_unknown_machine(base_game: GameVersion) -> None:
    patched = base_game.model_copy(
        update={"session": base_game.session.model_copy(update={"root_machine_id": "nope"})},
    )
    stack = ExecutionStack(max_depth=4)
    with pytest.raises(RuntimeError, match="unknown state machine"):
        stack.push_root(patched)


def test_stack_frames_property(base_game: GameVersion) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(base_game)
    assert stack.frames == (frame,)
    assert stack.depth == 1


def test_push_child_preserves_parent_context(nested_game: GameVersion) -> None:
    stack = ExecutionStack(max_depth=4)
    root = stack.push_root(nested_game)
    ctx = new_frame_context()
    ctx.respins_remaining = 3
    root.frame_context = ctx
    stack.push_child(nested_game, "hold_and_win")
    assert root.frame_context.respins_remaining == 3


def test_freeze_and_resume_noop_on_empty_stack() -> None:
    stack = ExecutionStack(max_depth=4)
    stack.freeze_top()
    stack.resume_parent()
