"""core.base-game plugin tests."""

from __future__ import annotations

import pytest

from runtime_core.domain.game_version import GameVersion
from runtime_core.plugins.base_game.grid import generate_grid
from runtime_core.plugins.base_game.lines import evaluate_line_wins
from runtime_core.plugins.base_game.plugin import BaseGamePlugin
from runtime_core.plugins.base_game.scatter import (
    evaluate_trigger_tokens,
    parse_symbol_triggers,
)
from runtime_core.plugins.bindings import plugin_game_bindings
from runtime_core.plugins.exceptions import PluginConfigurationError
from runtime_core.runtime.rng.service import RNGService
from tests.plugins.conftest import base_plugin_context


def _step_rng(seed: bytes):
    service = RNGService()
    scope = service.new_chain_scope(seed, 0, "test-run", 0)
    return scope.frame_stream("f-0-0").step_rng(0)


def test_reel_stops_are_deterministic(base_game: GameVersion) -> None:
    bindings = plugin_game_bindings(base_game)
    reel_set = bindings.reel_sets["base_game"]
    seed = b"fixture-01-determinism"

    rng_a = _step_rng(seed)
    grid_a = generate_grid(
        reel_set,
        grid_reels=bindings.grid_reels,
        grid_rows=bindings.grid_rows,
        rng=rng_a,
    )
    rng_b = _step_rng(seed)
    grid_b = generate_grid(
        reel_set,
        grid_reels=bindings.grid_reels,
        grid_rows=bindings.grid_rows,
        rng=rng_b,
    )

    assert grid_a.stops == grid_b.stops
    assert grid_a.symbols == grid_b.symbols
    assert grid_a.rng_draw_ids == grid_b.rng_draw_ids


def test_identical_seeds_produce_identical_grids_via_plugin(
    base_game: GameVersion,
) -> None:
    plugin = BaseGamePlugin()
    ctx = base_plugin_context(base_game)
    seed = b"fixture-01-plugin-grid"

    result_a = plugin.execute_step(ctx, _step_rng(seed))
    result_b = plugin.execute_step(ctx, _step_rng(seed))

    assert result_a.grid_outcome == result_b.grid_outcome


def test_payline_evaluation_five_h1_middle_row(base_game: GameVersion) -> None:
    bindings = plugin_game_bindings(base_game)
    symbols = [
        ["L1", "L1", "L1", "L1", "L1"],
        ["H1", "H1", "H1", "H1", "H1"],
        ["L1", "L1", "L1", "L1", "L1"],
    ]
    wins = evaluate_line_wins(
        symbols,
        bindings.paytable,
        bindings.win_model,
        bindings.bet_per_line_minor_units,
    )
    assert len(wins) == 1
    assert wins[0]["symbolId"] == "H1"
    assert wins[0]["count"] == 5
    assert wins[0]["winMinorUnits"] == 100 * bindings.bet_per_line_minor_units


def test_payline_no_win_when_count_insufficient(base_game: GameVersion) -> None:
    bindings = plugin_game_bindings(base_game)
    symbols = [
        ["L1", "L1", "L1", "L1", "L1"],
        ["H1", "H1", "H1", "L1", "L1"],
        ["L1", "L1", "L1", "L1", "L1"],
    ]
    wins = evaluate_line_wins(
        symbols,
        bindings.paytable,
        bindings.win_model,
        bindings.bet_per_line_minor_units,
    )
    assert wins == []


def test_scatter_trigger_emits_free_spins() -> None:
    symbols = [
        ["SCATTER", "L1", "L1", "L1", "L1"],
        ["L1", "SCATTER", "L1", "L1", "L1"],
        ["L1", "L1", "SCATTER", "L1", "L1"],
    ]
    rules = parse_symbol_triggers(
        [{"symbolId": "SCATTER", "minCount": 3, "emitTrigger": "FREE_SPINS"}],
    )
    tokens = evaluate_trigger_tokens(symbols, rules, ())
    assert tokens == ["FREE_SPINS"]


def test_scatter_below_threshold_emits_spin_complete() -> None:
    symbols = [
        ["SCATTER", "L1", "L1", "L1", "L1"],
        ["L1", "L1", "L1", "L1", "L1"],
        ["L1", "L1", "L1", "L1", "L1"],
    ]
    rules = parse_symbol_triggers(
        [{"symbolId": "SCATTER", "minCount": 3, "emitTrigger": "FREE_SPINS"}],
    )
    tokens = evaluate_trigger_tokens(symbols, rules, ())
    assert tokens == ["SPIN_COMPLETE"]


def test_execute_step_requires_game_bindings(base_game: GameVersion) -> None:
    plugin = BaseGamePlugin()
    ctx = base_plugin_context(base_game)
    ctx = type(ctx)(
        plugin_id=ctx.plugin_id,
        plugin_version=ctx.plugin_version,
        config_schema_version=ctx.config_schema_version,
        plugin_config=ctx.plugin_config,
        frame_context=ctx.frame_context,
        rtp_category=ctx.rtp_category,
        frame_id=ctx.frame_id,
        machine_id=ctx.machine_id,
        state_id=ctx.state_id,
        plugin_ref_id=ctx.plugin_ref_id,
        game_bindings=None,
    )
    with pytest.raises(PluginConfigurationError, match="game_bindings"):
        plugin.execute_step(ctx, _step_rng(b"seed"))


def test_unknown_reel_set_raises(base_game: GameVersion) -> None:
    plugin = BaseGamePlugin()
    ctx = base_plugin_context(
        base_game,
        plugin_config={"reelSetId": "missing", "scatterTriggers": []},
    )
    with pytest.raises(PluginConfigurationError, match="unknown reelSetId"):
        plugin.execute_step(ctx, _step_rng(b"seed"))


def test_grid_outcome_shape(base_game: GameVersion) -> None:
    plugin = BaseGamePlugin()
    ctx = base_plugin_context(base_game)
    result = plugin.execute_step(ctx, _step_rng(b"grid-shape"))
    assert result.grid_outcome is not None
    assert result.grid_outcome["reelSetId"] == "base_game"
    assert len(result.grid_outcome["symbols"]) == 3
    assert len(result.grid_outcome["symbols"][0]) == 5
    assert len(result.grid_outcome["rngDrawIds"]) == 5
