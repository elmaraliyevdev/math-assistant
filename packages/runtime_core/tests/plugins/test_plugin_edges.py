"""Additional coverage for plugin implementation edge cases."""

from __future__ import annotations

import pytest

from runtime_core.domain.plugins import Paytable, PaylineDefinition, PaytableEntry, ReelSet, ReelStrip, WinModel
from runtime_core.plugins.base_game.grid import generate_grid
from runtime_core.plugins.base_game.lines import evaluate_line_wins
from runtime_core.plugins.base_game.scatter import evaluate_trigger_tokens, parse_symbol_triggers
from runtime_core.plugins.bindings import plugin_game_bindings
from runtime_core.plugins.multiplier.apply import apply_multiplier
from runtime_core.plugins.multiplier.config import parse_multiplier_config
from runtime_core.plugins.multiplier.plugin import MultiplierPlugin
from runtime_core.runtime.frames import new_frame_context
from runtime_core.runtime.rng.protocol import RNG


class _FixedRNG:
    __slots__ = ("_value", "_draw_id")

    def __init__(self, value: int = 0) -> None:
        self._value = value
        self._draw_id = 0

    def next_uint64(self) -> int:
        self._draw_id += 1
        return 0

    def next_int(self, n: int) -> int:
        self._draw_id += 1
        if n <= 1:
            return 0
        return min(self._value, n - 1)

    @property
    def draw_id(self) -> int:
        return self._draw_id


def test_generate_grid_rejects_reel_count_mismatch() -> None:
    reel_set = ReelSet(
        id="bad",
        reels=[ReelStrip(reel_index=0, symbols=["H1"])],
    )
    with pytest.raises(ValueError, match="expected 5"):
        generate_grid(reel_set, grid_reels=5, grid_rows=3, rng=_FixedRNG())


def test_generate_grid_rejects_empty_strip() -> None:
    reel_set = ReelSet(
        id="empty",
        reels=[ReelStrip(reel_index=0, symbols=[])],
    )
    with pytest.raises(ValueError, match="empty"):
        generate_grid(reel_set, grid_reels=1, grid_rows=3, rng=_FixedRNG())


def test_evaluate_line_wins_non_lines_model_returns_empty() -> None:
    paytable = Paytable(
        lines=[PaylineDefinition(index=1, path=[0, 0, 0])],
        pays=[PaytableEntry(symbol_id="H1", count=3, multiplier=10)],
    )
    wins = evaluate_line_wins(
        [["H1", "H1", "H1"]],
        paytable,
        WinModel(type="ways"),
        100,
    )
    assert wins == []


def test_bonus_trigger_emits_token() -> None:
    symbols = [["BONUS"] * 3]
    bonus = parse_symbol_triggers(
        [{"symbolId": "BONUS", "minCount": 3, "emitTrigger": "HOLD_AND_WIN"}],
    )
    tokens = evaluate_trigger_tokens(symbols, (), bonus)
    assert tokens == ["HOLD_AND_WIN"]


def test_plugin_game_bindings_accepts_total_bet_override(base_game) -> None:
    bindings = plugin_game_bindings(base_game, total_bet_minor_units=4000)
    assert bindings.bet_per_line_minor_units == 200


def test_ladder_multiplier_mode() -> None:
    config = parse_multiplier_config(
        {
            "mode": "ladder",
            "value": 1,
            "scope": "feature_frame",
            "applyTo": "all_wins_in_frame",
            "ladder": [2, 4, 8],
        },
    )
    wins = [{"source": "lines", "symbolId": "H1", "count": 5, "winMinorUnits": 100}]
    result = apply_multiplier(config, wins, _FixedRNG(1))
    assert result.factor == 4
    assert result.wins[0]["winMinorUnits"] == 400


def test_multiplier_execute_step_with_pending_wins() -> None:
    plugin = MultiplierPlugin()
    ctx_frame = new_frame_context()
    ctx_frame.frame_local_state["pendingWins"] = [
        {"source": "lines", "symbolId": "H1", "count": 5, "winMinorUnits": 100},
    ]
    from runtime_core.plugins.contracts import PluginContext

    ctx = PluginContext(
        plugin_id="core.multiplier",
        plugin_version="1.0.0",
        config_schema_version="1.0.0",
        plugin_config={
            "mode": "fixed",
            "value": 2,
            "scope": "feature_frame",
            "applyTo": "all_wins_in_frame",
        },
        frame_context=ctx_frame,
        rtp_category="BASE",
        frame_id="f-0-0",
        machine_id="main",
        state_id="BASE",
        plugin_ref_id="mult",
    )
    result = plugin.execute_step(ctx, _FixedRNG())
    assert result.wins[0]["winMinorUnits"] == 200


def test_evaluate_line_wins_skips_empty_line_symbols() -> None:
    paytable = Paytable(
        lines=[PaylineDefinition(index=1, path=[0, 0, 0])],
        pays=[PaytableEntry(symbol_id="H1", count=3, multiplier=10)],
    )
    wins = evaluate_line_wins(
        [],
        paytable,
        WinModel(type="lines"),
        100,
    )
    assert wins == []


def test_evaluate_line_wins_float_multiplier_rounds() -> None:
    paytable = Paytable(
        lines=[PaylineDefinition(index=1, path=[0, 0, 0])],
        pays=[PaytableEntry(symbol_id="H1", count=3, multiplier=10.6)],
    )
    wins = evaluate_line_wins(
        [["H1", "H1", "H1"]],
        paytable,
        WinModel(type="lines"),
        100,
    )
    assert wins[0]["winMinorUnits"] == 1100


def test_evaluate_line_wins_skips_out_of_bounds_path() -> None:
    paytable = Paytable(
        lines=[PaylineDefinition(index=1, path=[9, 9, 9])],
        pays=[PaytableEntry(symbol_id="H1", count=3, multiplier=10)],
    )
    wins = evaluate_line_wins(
        [["H1", "H1", "H1"]],
        paytable,
        WinModel(type="lines"),
        100,
    )
    assert wins == []


def test_plugin_game_bindings_defaults_line_count_when_zero(base_game) -> None:
    game = base_game.model_copy(
        update={
            "bet_model": base_game.bet_model.model_copy(update={"line_count": 0}),
        },
    )
    bindings = plugin_game_bindings(game)
    assert bindings.bet_per_line_minor_units > 0


def test_multiplier_ladder_missing_at_apply_time_raises() -> None:
    config = parse_multiplier_config(
        {
            "mode": "fixed",
            "value": 1,
            "scope": "feature_frame",
            "applyTo": "all_wins_in_frame",
        },
    )
    broken = config.__class__(
        mode="ladder",
        value=1,
        scope="feature_frame",
        apply_to="all_wins_in_frame",
        ladder=(),
        weights=(),
    )
    with pytest.raises(ValueError, match="ladder"):
        apply_multiplier(
            broken,
            [{"source": "lines", "symbolId": "H1", "count": 5, "winMinorUnits": 100}],
            _FixedRNG(),
        )


def test_multiplier_weighted_zero_total_raises() -> None:
    config = parse_multiplier_config(
        {
            "mode": "random_weighted",
            "value": 2,
            "scope": "feature_frame",
            "applyTo": "all_wins_in_frame",
            "weights": [0, 0, 0],
        },
    )
    with pytest.raises(ValueError, match="positive"):
        apply_multiplier(
            config,
            [{"source": "lines", "symbolId": "H1", "count": 5, "winMinorUnits": 100}],
            _FixedRNG(),
        )


def test_multiplier_random_weighted_missing_weights_at_apply_raises() -> None:
    config = parse_multiplier_config(
        {
            "mode": "random_weighted",
            "value": 2,
            "scope": "feature_frame",
            "applyTo": "all_wins_in_frame",
            "weights": [1],
        },
    )
    broken = config.__class__(
        mode="random_weighted",
        value=2,
        scope="feature_frame",
        apply_to="all_wins_in_frame",
        ladder=(),
        weights=(),
    )
    with pytest.raises(ValueError, match="weights"):
        apply_multiplier(
            broken,
            [{"source": "lines", "symbolId": "H1", "count": 5, "winMinorUnits": 100}],
            _FixedRNG(),
        )


def test_multiplier_plugin_lifecycle_hooks_are_noops() -> None:
    plugin = MultiplierPlugin()
    from runtime_core.plugins.contracts import PluginContext

    ctx = PluginContext(
        plugin_id="core.multiplier",
        plugin_version="1.0.0",
        config_schema_version="1.0.0",
        plugin_config={},
        frame_context=new_frame_context(),
        rtp_category="BASE",
        frame_id="f-0-0",
        machine_id="main",
        state_id="BASE",
        plugin_ref_id="mult",
    )
    plugin.on_enter(ctx)
    plugin.on_exit(ctx)


def test_ladder_mode_requires_ladder_in_config() -> None:
    with pytest.raises(Exception, match="ladder"):
        parse_multiplier_config(
            {
                "mode": "ladder",
                "value": 1,
                "scope": "feature_frame",
                "applyTo": "all_wins_in_frame",
            },
        )
