"""Golden fixture integration for Hold & Win lifecycle."""

from __future__ import annotations

import pytest

from runtime_core.common.golden import load_golden_game_version
from runtime_core.domain.game_version import GameVersion
from runtime_core.plugins.bindings import plugin_game_bindings
from runtime_core.runtime.lifecycle import apply_transition
from runtime_core.runtime.plugins.counters import apply_step_side_effects
from runtime_core.runtime.plugins.host import PluginHost
from runtime_core.runtime.rng.service import RNGService
from runtime_core.runtime.stack import ExecutionStack
from runtime_core.runtime.transitions import resolve_transition
from runtime_core.validation.validators.priority_tiers import PriorityTierRegistry


@pytest.fixture
def haw_game() -> GameVersion:
    return load_golden_game_version("fixture-03-base-hold-win")


def _resolve_and_apply(game, stack, frame, tokens, tiers):
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


def _seed_haw_entry(parent_frame, child_frame) -> None:
    held = parent_frame.frame_context.frame_local_state.get("entryHeldSymbols")
    if isinstance(held, list):
        child_frame.frame_context.frame_local_state["entryHeldSymbols"] = held


@pytest.mark.golden
def test_fixture_03_forced_hold_and_win_lifecycle(
    haw_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=haw_game.session.max_stack_depth)
    root = stack.push_root(haw_game)
    root.frame_context.frame_local_state["entryHeldSymbols"] = [
        {"reel": index % 5, "row": 0, "symbolId": "BONUS"}
        for index in range(6)
    ]

    spawn = _resolve_and_apply(
        haw_game,
        stack,
        root,
        ["HOLD_AND_WIN"],
        priority_tiers,
    )
    assert spawn.effect == "spawn"
    assert stack.depth == 2
    child = stack.top()
    assert child is not None
    assert child.state_id == "HAW_RESPINS"
    _seed_haw_entry(root, child)

    haw_state = haw_game.state_machines["hold_and_win"].states["HAW_RESPINS"]
    host = PluginHost()
    handle = host.bind(
        haw_game.plugins[haw_state.plugin_ref_id],
        child,
        plugin_config=dict(haw_state.plugin_config or {}),
        game_bindings=plugin_game_bindings(haw_game),
    )
    host.apply_enter_result(handle)
    assert handle.context.frame_context.respins_remaining == 3

    service = RNGService()
    scope = service.new_chain_scope(b"fixture-03-forced", 0, "golden", 0)
    step = 0
    complete_tokens: list[str] = []
    while step < 200:
        result = host.execute_step(
            handle,
            scope.frame_stream(child.frame_id).step_rng(step),
        )
        apply_step_side_effects(handle.context.frame_context, result)
        step += 1
        if "FEATURE_COMPLETE" in result.trigger_tokens:
            complete_tokens = result.trigger_tokens
            break
    else:
        pytest.fail("hold and win did not complete")

    host.release(handle)
    pop = _resolve_and_apply(
        haw_game,
        stack,
        stack.top(),
        complete_tokens,
        priority_tiers,
    )
    assert pop.effect == "pop"
    assert stack.depth == 1
    assert stack.top() is not None
    assert stack.top().state_id == "BASE"


@pytest.mark.golden
def test_fixture_03_loads(haw_game: GameVersion) -> None:
    assert "hold_and_win" in haw_game.state_machines
    assert haw_game.state_machines["hold_and_win"].states["HAW_RESPINS"].plugin_ref_id == "haw_main"
