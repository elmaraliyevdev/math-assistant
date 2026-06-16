"""Golden fixture integration for Free Spins lifecycle."""

from __future__ import annotations

import pytest

from runtime_core.common.golden import load_golden_game_version
from runtime_core.domain.game_version import GameVersion
from runtime_core.plugins.base_game.plugin import BaseGamePlugin
from runtime_core.plugins.bindings import plugin_game_bindings
from runtime_core.runtime.lifecycle import apply_transition
from runtime_core.runtime.plugins.counters import apply_step_side_effects
from runtime_core.runtime.plugins.host import PluginHost
from runtime_core.runtime.rng.service import RNGService
from runtime_core.runtime.stack import ExecutionStack
from runtime_core.runtime.transitions import resolve_transition
from runtime_core.validation.validators.priority_tiers import PriorityTierRegistry
from tests.plugins.conftest import base_plugin_context


@pytest.fixture
def fs_game() -> GameVersion:
    return load_golden_game_version("fixture-02-base-free-spins")


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


@pytest.mark.golden
def test_fixture_02_full_free_spins_lifecycle(
    fs_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=fs_game.session.max_stack_depth)
    frame = stack.push_root(fs_game)
    service = RNGService()
    scope = service.new_chain_scope(b"fixture-02-lifecycle", 0, "golden", 0)

    base_ctx = base_plugin_context(fs_game)
    base_result = BaseGamePlugin().execute_step(
        base_ctx,
        scope.frame_stream(frame.frame_id).step_rng(0),
    )
    apply_step_side_effects(frame.frame_context, base_result)

    if "FREE_SPINS" not in base_result.trigger_tokens:
        pytest.skip("seed did not produce FREE_SPINS entry in this run")

    goto_fs = _resolve_and_apply(
        fs_game,
        stack,
        frame,
        base_result.trigger_tokens,
        priority_tiers,
    )
    assert goto_fs.effect == "goto"
    assert stack.top() is not None
    assert stack.top().state_id == "FREE_SPINS"

    fs_state = fs_game.state_machines["main"].states["FREE_SPINS"]
    fs_ref = fs_game.plugins[fs_state.plugin_ref_id]
    host = PluginHost()
    handle = host.bind(
        fs_ref,
        stack.top(),
        plugin_config=dict(fs_state.plugin_config or {}),
        game_bindings=plugin_game_bindings(fs_game),
    )
    enter = host.apply_enter_result(handle)
    assert enter is not None
    scatter_count = int(
        handle.context.frame_context.frame_local_state["entryScatterCount"],
    )
    expected = fs_state.plugin_config["awardsByScatterCount"][str(scatter_count)]
    assert handle.context.frame_context.spins_remaining == expected

    step_index = 1
    complete_tokens: list[str] = []
    while True:
        fs_result = host.execute_step(
            handle,
            scope.frame_stream(frame.frame_id).step_rng(step_index),
        )
        apply_step_side_effects(handle.context.frame_context, fs_result)
        step_index += 1
        if "FEATURE_COMPLETE" in fs_result.trigger_tokens:
            complete_tokens = fs_result.trigger_tokens
            break
        if step_index > 200:
            pytest.fail("free spins loop did not complete")

    host.release(handle)
    complete = _resolve_and_apply(
        fs_game,
        stack,
        stack.top(),
        complete_tokens,
        priority_tiers,
    )
    assert complete.effect == "goto"
    assert stack.top() is not None
    assert stack.top().state_id == "BASE"


@pytest.mark.golden
def test_fixture_02_loads_and_validates(fs_game: GameVersion) -> None:
    assert fs_game.state_machines["main"].states["FREE_SPINS"].plugin_ref_id == "fs_main"
    assert "free_spins" in fs_game.reel_sets


@pytest.mark.golden
def test_fixture_02_forced_entry_lifecycle(
    fs_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    """Deterministic BASE → FREE_SPINS → BASE without relying on base spin RNG."""
    stack = ExecutionStack(max_depth=fs_game.session.max_stack_depth)
    frame = stack.push_root(fs_game)
    frame.frame_context.frame_local_state["scatterCounts"] = {"SCATTER": 3}

    goto_fs = _resolve_and_apply(
        fs_game,
        stack,
        frame,
        ["FREE_SPINS"],
        priority_tiers,
    )
    assert goto_fs.state_changed
    assert stack.top().state_id == "FREE_SPINS"

    fs_state = fs_game.state_machines["main"].states["FREE_SPINS"]
    host = PluginHost()
    handle = host.bind(
        fs_game.plugins[fs_state.plugin_ref_id],
        stack.top(),
        plugin_config=dict(fs_state.plugin_config or {}),
        game_bindings=plugin_game_bindings(fs_game),
    )
    host.apply_enter_result(handle)
    assert handle.context.frame_context.spins_remaining == 10

    service = RNGService()
    scope = service.new_chain_scope(b"fixture-02-forced", 0, "golden", 0)
    spins_left = handle.context.frame_context.spins_remaining
    step = 0
    while spins_left > 0:
        result = host.execute_step(
            handle,
            scope.frame_stream(stack.top().frame_id).step_rng(step),
        )
        apply_step_side_effects(handle.context.frame_context, result)
        spins_left = handle.context.frame_context.spins_remaining
        step += 1
        if "FEATURE_COMPLETE" in result.trigger_tokens:
            break

    assert handle.context.frame_context.spins_remaining == 0
    host.release(handle)

    back = _resolve_and_apply(
        fs_game,
        stack,
        stack.top(),
        ["FEATURE_COMPLETE"],
        priority_tiers,
    )
    assert back.effect == "goto"
    assert stack.top().state_id == "BASE"
