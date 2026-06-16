"""PluginHost enter_result integration tests."""

from __future__ import annotations

from runtime_core.common.golden import load_golden_game_version
from runtime_core.plugins.bindings import plugin_game_bindings
from runtime_core.runtime.plugins.host import PluginHost
from runtime_core.runtime.stack import ExecutionStack


def test_host_apply_enter_result_for_free_spins() -> None:
    game = load_golden_game_version("fixture-02-base-free-spins")
    stack = ExecutionStack(max_depth=game.session.max_stack_depth)
    frame = stack.push_root(game)
    frame.frame_context.frame_local_state["scatterCounts"] = {"SCATTER": 3}

    fs_state = game.state_machines["main"].states["FREE_SPINS"]
    from runtime_core.runtime.lifecycle import apply_transition
    from runtime_core.runtime.transitions import resolve_transition
    from runtime_core.validation.validators.priority_tiers import PriorityTierRegistry

    tiers = PriorityTierRegistry.load(
        __import__(
            "runtime_core.common.paths",
            fromlist=["game_schema_root"],
        ).game_schema_root(),
    )
    resolution = resolve_transition(game, frame, ["FREE_SPINS"], tiers)
    assert resolution.resolution is not None
    outcome = apply_transition(
        stack,
        game,
        frame,
        resolution.resolution.transition,
    )
    assert outcome.state_changed

    host = PluginHost()
    handle = host.bind(
        game.plugins[fs_state.plugin_ref_id],
        stack.top(),
        plugin_config=dict(fs_state.plugin_config or {}),
        game_bindings=plugin_game_bindings(game),
    )
    enter = host.apply_enter_result(handle)
    assert enter is not None
    assert handle.context.frame_context.spins_remaining == 10
    host.release(handle)
