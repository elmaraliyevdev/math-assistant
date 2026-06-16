"""core.hold-and-win plugin tests."""

from __future__ import annotations

import pytest

from runtime_core.common.golden import load_golden_game_version
from runtime_core.domain.game_version import GameVersion
from runtime_core.domain.plugins import ReelSet, ReelStrip
from runtime_core.plugins.bindings import plugin_game_bindings
from runtime_core.plugins.contracts import CounterUpdateRequest, PluginContext
from runtime_core.plugins.exceptions import PluginConfigurationError
from runtime_core.plugins.hold_and_win.config import (
    parse_hold_and_win_config,
    qualifying_jackpot_tier,
)
from runtime_core.plugins.hold_and_win.grid import generate_respin_lands, normalize_held_symbols
from runtime_core.plugins.hold_and_win.lifecycle import build_enter_result, finalize_step_result
from runtime_core.plugins.hold_and_win.plugin import HoldAndWinPlugin
from runtime_core.plugins.hold_and_win.wins import evaluate_hold_and_win_wins, initial_jackpot_tracking
from runtime_core.runtime.frames import new_frame_context
from runtime_core.runtime.plugins.counters import apply_step_side_effects
from runtime_core.runtime.rng.service import RNGService
from runtime_core.runtime.stack import build_frame


class _FixedRNG:
    __slots__ = ("_values", "_index", "_draw_id")

    def __init__(self, values: list[int]) -> None:
        self._values = values
        self._index = 0
        self._draw_id = 0

    def next_uint64(self) -> int:
        self._draw_id += 1
        return 0

    def next_int(self, n: int) -> int:
        self._draw_id += 1
        value = self._values[self._index]
        self._index = min(self._index + 1, len(self._values) - 1)
        if n <= 1:
            return 0
        return min(value, n - 1)

    @property
    def draw_id(self) -> int:
        return self._draw_id


@pytest.fixture
def haw_game() -> GameVersion:
    return load_golden_game_version("fixture-03-base-hold-win")


def _haw_config(game: GameVersion) -> dict[str, object]:
    return dict(
        game.state_machines["hold_and_win"].states["HAW_RESPINS"].plugin_config or {},
    )


def _entry_held(count: int = 6) -> list[dict[str, int | str]]:
    return [
        {"reel": index % 5, "row": index // 5, "symbolId": "BONUS"}
        for index in range(count)
    ]


def _haw_context(game: GameVersion) -> PluginContext:
    state = game.state_machines["hold_and_win"].states["HAW_RESPINS"]
    ref = game.plugins[state.plugin_ref_id]
    frame = build_frame(
        frame_id="f-1-0",
        machine_id="hold_and_win",
        state=state,
        frame_context=new_frame_context(),
    )
    frame.frame_context.frame_local_state["entryHeldSymbols"] = _entry_held()
    return PluginContext(
        plugin_id=ref.plugin_id,
        plugin_version=ref.plugin_version,
        config_schema_version=ref.config_schema_version,
        plugin_config=_haw_config(game),
        frame_context=frame.frame_context,
        rtp_category="HOLD_AND_WIN",
        frame_id=frame.frame_id,
        machine_id=frame.machine_id,
        state_id=frame.state_id,
        plugin_ref_id=ref.ref_id,
        game_bindings=plugin_game_bindings(game),
    )


def test_initialization_sets_respins_and_held_symbols(haw_game: GameVersion) -> None:
    ctx = _haw_context(haw_game)
    config = parse_hold_and_win_config(ctx.plugin_config)
    enter = build_enter_result(ctx, config)
    assert enter.counter_updates == [
        CounterUpdateRequest(field="respinsRemaining", after=3),
    ]
    apply_step_side_effects(ctx.frame_context, enter)
    assert len(ctx.frame_context.frame_local_state["heldSymbols"]) == 6
    assert ctx.frame_context.respins_remaining == 3
    assert ctx.frame_context.frame_local_state["jackpotTracking"] == {
        "mini": False,
        "major": False,
        "grand": False,
    }


def test_respin_resets_counter_when_new_symbol_lands(haw_game: GameVersion) -> None:
    ctx = _haw_context(haw_game)
    config = parse_hold_and_win_config(ctx.plugin_config)
    apply_step_side_effects(ctx.frame_context, build_enter_result(ctx, config))
    reel_set = haw_game.reel_sets["hold_and_win"]
    held = normalize_held_symbols(ctx.frame_context.frame_local_state["heldSymbols"])
    # stop=0 on each reel at row 0 yields BONUS on reel 0 row 0 (empty)
    respin = generate_respin_lands(
        config,
        reel_set,
        grid_reels=5,
        grid_rows=3,
        held_symbols=held,
        rng=_FixedRNG([0] * 20),
    )
    assert respin.new_symbols
    result = finalize_step_result(
        config=config,
        held_before=held,
        new_symbols=respin.new_symbols,
        respins_before=ctx.frame_context.respins_remaining,
        step_count=0,
        max_steps=500,
        total_bet_minor_units=2000,
        jackpot_tracking=initial_jackpot_tracking(config),
        rng_draw_ids=respin.rng_draw_ids,
    )
    assert result.counter_updates[-1].after == 3


def test_respin_decrements_when_no_new_symbols(haw_game: GameVersion) -> None:
    ctx = _haw_context(haw_game)
    config = parse_hold_and_win_config(ctx.plugin_config)
    apply_step_side_effects(ctx.frame_context, build_enter_result(ctx, config))
    held = normalize_held_symbols(ctx.frame_context.frame_local_state["heldSymbols"])
    result = finalize_step_result(
        config=config,
        held_before=held,
        new_symbols=[],
        respins_before=3,
        step_count=0,
        max_steps=500,
        total_bet_minor_units=2000,
        jackpot_tracking=initial_jackpot_tracking(config),
        rng_draw_ids=[],
    )
    assert result.counter_updates[-1].after == 2
    assert "FEATURE_COMPLETE" not in result.trigger_tokens


def test_feature_complete_at_zero_respins(haw_game: GameVersion) -> None:
    config = parse_hold_and_win_config(_haw_config(haw_game))
    held = normalize_held_symbols(_entry_held())
    result = finalize_step_result(
        config=config,
        held_before=held,
        new_symbols=[],
        respins_before=1,
        step_count=0,
        max_steps=500,
        total_bet_minor_units=2000,
        jackpot_tracking=initial_jackpot_tracking(config),
        rng_draw_ids=[],
    )
    assert "FEATURE_COMPLETE" in result.trigger_tokens
    assert result.counter_updates[-1].after == 0
    assert result.wins


def test_feature_complete_at_full_grid(haw_game: GameVersion) -> None:
    config = parse_hold_and_win_config(_haw_config(haw_game))
    held = normalize_held_symbols(_entry_held(count=15))
    for symbol in held:
        symbol["valueMultiplier"] = 2
    result = finalize_step_result(
        config=config,
        held_before=held,
        new_symbols=[],
        respins_before=2,
        step_count=0,
        max_steps=500,
        total_bet_minor_units=2000,
        jackpot_tracking=initial_jackpot_tracking(config),
        rng_draw_ids=[],
    )
    assert "FEATURE_COMPLETE" in result.trigger_tokens
    assert any(win["source"] == "jackpot" and win["symbolId"] == "grand" for win in result.wins)


def test_jackpot_evaluation_major_tier(haw_game: GameVersion) -> None:
    config = parse_hold_and_win_config(_haw_config(haw_game))
    held = normalize_held_symbols(_entry_held(count=14))
    wins, tracking = evaluate_hold_and_win_wins(
        config,
        held,
        total_bet_minor_units=2000,
        jackpot_tracking=initial_jackpot_tracking(config),
    )
    assert qualifying_jackpot_tier(config, 14) == "major"
    assert any(win["source"] == "jackpot" and win["symbolId"] == "major" for win in wins)
    assert tracking["major"] is True


def test_deterministic_hold_and_win_outcomes(haw_game: GameVersion) -> None:
    plugin = HoldAndWinPlugin()
    seed = b"fixture-03-determinism"
    service = RNGService()

    def run_chain() -> list[object]:
        ctx = _haw_context(haw_game)
        apply_step_side_effects(
            ctx.frame_context,
            build_enter_result(ctx, parse_hold_and_win_config(ctx.plugin_config)),
        )
        outcomes: list[object] = []
        for step in range(3):
            scope = service.new_chain_scope(seed, 0, "haw", 0)
            result = plugin.execute_step(
                ctx,
                scope.frame_stream(ctx.frame_id).step_rng(step),
            )
            apply_step_side_effects(ctx.frame_context, result)
            outcomes.append(result.grid_outcome)
        return outcomes

    assert run_chain() == run_chain()


def test_plugin_execute_requires_game_bindings(haw_game: GameVersion) -> None:
    ctx = _haw_context(haw_game)
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
        HoldAndWinPlugin().execute_step(ctx, _FixedRNG([0]))


def test_entry_requires_minimum_trigger_symbols(haw_game: GameVersion) -> None:
    ctx = _haw_context(haw_game)
    ctx.frame_context.frame_local_state["entryHeldSymbols"] = _entry_held(count=5)
    config = parse_hold_and_win_config(ctx.plugin_config)
    with pytest.raises(PluginConfigurationError, match="at least 6"):
        build_enter_result(ctx, config)
