"""Golden fixture integration for built-in base-game plugin."""

from __future__ import annotations

import pytest

from runtime_core.common.golden import load_golden_game_version
from runtime_core.domain.game_version import GameVersion
from runtime_core.plugins.base_game.plugin import BaseGamePlugin
from runtime_core.runtime.plugins.host import PluginHost
from runtime_core.runtime.rng.service import RNGService
from runtime_core.runtime.session.resolution import resolve_bet
from runtime_core.runtime.stack import ExecutionStack
from runtime_core.runtime.transitions import resolve_transition
from runtime_core.validation.validators.priority_tiers import PriorityTierRegistry
from tests.plugins.conftest import base_plugin_context


@pytest.mark.golden
def test_fixture_01_base_game_deterministic_grid() -> None:
    game = load_golden_game_version("fixture-01-base-5x3")
    ctx = base_plugin_context(game)
    plugin = BaseGamePlugin()
    seed = b"golden-fixture-01-grid"

    service = RNGService()
    scope = service.new_chain_scope(seed, 0, "golden", 0)
    rng_a = scope.frame_stream("f-0-0").step_rng(0)
    rng_b = scope.frame_stream("f-0-0").step_rng(0)

    outcome_a = plugin.execute_step(ctx, rng_a)
    outcome_b = plugin.execute_step(ctx, rng_b)

    assert outcome_a.grid_outcome == outcome_b.grid_outcome
    assert outcome_a.grid_outcome is not None
    assert outcome_a.grid_outcome["reelSetId"] == "base_game"


@pytest.mark.golden
def test_fixture_01_plugin_host_bind_and_execute(base_game: GameVersion) -> None:
    machine = base_game.state_machines["main"]
    state = machine.states["BASE"]
    plugin_ref = base_game.plugins[state.plugin_ref_id]
    stack = ExecutionStack(max_depth=base_game.session.max_stack_depth)
    frame = stack.push_root(base_game)

    host = PluginHost()
    from runtime_core.plugins.bindings import plugin_game_bindings

    handle = host.bind(
        plugin_ref,
        frame,
        plugin_config=dict(state.plugin_config or {}),
        game_bindings=plugin_game_bindings(base_game),
    )
    service = RNGService()
    scope = service.new_chain_scope(b"golden-host", 0, "golden", 0)
    result = host.execute_step(handle, scope.frame_stream(frame.frame_id).step_rng(0))
    host.release(handle)

    assert result.grid_outcome is not None
    assert len(result.grid_outcome["symbols"]) == base_game.game_config.grid.rows
    assert result.trigger_tokens
    assert result.trigger_tokens[0] in {"SPIN_COMPLETE", "FREE_SPINS"}


@pytest.mark.golden
def test_fixture_01_spin_complete_transition_when_no_feature(
    base_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    plugin = BaseGamePlugin()
    ctx = base_plugin_context(
        base_game,
        plugin_config={"reelSetId": "base_game", "scatterTriggers": []},
    )
    service = RNGService()
    scope = service.new_chain_scope(b"golden-transition", 0, "golden", 0)
    step = plugin.execute_step(ctx, scope.frame_stream("f-0-0").step_rng(0))

    stack = ExecutionStack(max_depth=base_game.session.max_stack_depth)
    frame = stack.push_root(base_game)
    resolution = resolve_transition(
        base_game,
        frame,
        step.trigger_tokens,
        priority_tiers,
    )
    assert resolution.fault is None
    assert resolution.resolution is not None
    assert resolution.resolution.transition.trigger == "SPIN_COMPLETE"


@pytest.mark.golden
def test_fixture_01_bet_per_line_matches_bet_model(base_game: GameVersion) -> None:
    from runtime_core.plugins.bindings import plugin_game_bindings

    _, total_bet = resolve_bet(base_game, 0)
    bindings = plugin_game_bindings(base_game)
    lines = base_game.bet_model.line_count or 1
    assert bindings.bet_per_line_minor_units * lines == total_bet
