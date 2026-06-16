"""Additional Hold & Win edge-case coverage."""

from __future__ import annotations

import pytest

from runtime_core.domain.plugins import ReelSet, ReelStrip
from runtime_core.plugins.exceptions import PluginConfigurationError
from runtime_core.plugins.hold_and_win.config import jackpot_threshold, parse_hold_and_win_config
from runtime_core.plugins.hold_and_win.grid import generate_respin_lands, normalize_held_symbols
from runtime_core.plugins.hold_and_win.plugin import HoldAndWinPlugin
from runtime_core.plugins.contracts import PluginContext
from runtime_core.runtime.frames import new_frame_context


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
        return 0 if n <= 1 else min(self._value, n - 1)

    @property
    def draw_id(self) -> int:
        return self._draw_id


def test_generate_respin_skips_when_grid_full() -> None:
    config = parse_hold_and_win_config(
        {
            "reelSetId": "hold_and_win",
            "triggerSymbolId": "BONUS",
            "triggerSymbolCount": 6,
            "initialRespins": 3,
            "gridCapacity": 2,
        },
    )
    reel_set = ReelSet(
        id="hold_and_win",
        reels=[ReelStrip(reel_index=0, symbols=["BONUS", "L1"])],
    )
    held = [{"reel": 0, "row": 0, "symbolId": "BONUS", "valueMultiplier": 1}]
    respin = generate_respin_lands(
        config,
        reel_set,
        grid_reels=1,
        grid_rows=1,
        held_symbols=normalize_held_symbols(held),
        rng=_FixedRNG(),
    )
    assert respin.new_symbols == []


def test_jackpot_threshold_grand_requires_full_grid() -> None:
    config = parse_hold_and_win_config(
        {
            "reelSetId": "hold_and_win",
            "triggerSymbolId": "BONUS",
            "triggerSymbolCount": 6,
            "initialRespins": 3,
            "gridCapacity": 15,
            "jackpotTiers": {"grand": 500},
        },
    )
    assert jackpot_threshold(config, "grand") == 15


def test_plugin_on_enter_and_exit_hooks() -> None:
    plugin = HoldAndWinPlugin()
    ctx = PluginContext(
        plugin_id="core.hold-and-win",
        plugin_version="1.0.0",
        config_schema_version="1.0.0",
        plugin_config={
            "reelSetId": "hold_and_win",
            "triggerSymbolId": "BONUS",
            "triggerSymbolCount": 1,
            "initialRespins": 3,
            "gridCapacity": 15,
        },
        frame_context=new_frame_context(),
        rtp_category="HOLD_AND_WIN",
        frame_id="f-1-0",
        machine_id="hold_and_win",
        state_id="HAW_RESPINS",
        plugin_ref_id="haw",
    )
    ctx.frame_context.frame_local_state["entryHeldSymbols"] = [
        {"reel": 0, "row": 0, "symbolId": "BONUS"},
    ]
    plugin.on_enter(ctx)
    assert plugin.enter_result() is not None
    plugin.on_exit(ctx)


def test_parse_config_invalid_jackpot_tier_threshold_raises() -> None:
    config = parse_hold_and_win_config(
        {
            "reelSetId": "hold_and_win",
            "triggerSymbolId": "BONUS",
            "triggerSymbolCount": 6,
            "initialRespins": 3,
            "gridCapacity": 15,
        },
    )
    with pytest.raises(PluginConfigurationError):
        jackpot_threshold(config, "unknown")


def test_normalize_held_symbols_skips_invalid_items() -> None:
    held = normalize_held_symbols(["bad", {"reel": 0, "row": 0, "symbolId": "BONUS"}])
    assert len(held) == 1


def test_finalize_step_result_clamps_held_to_capacity() -> None:
    from runtime_core.plugins.hold_and_win.config import parse_hold_and_win_config
    from runtime_core.plugins.hold_and_win.lifecycle import finalize_step_result
    from runtime_core.plugins.hold_and_win.wins import initial_jackpot_tracking

    config = parse_hold_and_win_config(
        {
            "reelSetId": "hold_and_win",
            "triggerSymbolId": "BONUS",
            "triggerSymbolCount": 1,
            "initialRespins": 3,
            "gridCapacity": 2,
        },
    )
    held = [
        {"reel": 0, "row": 0, "symbolId": "BONUS", "valueMultiplier": 1},
    ]
    new = [
        {"reel": 1, "row": 0, "symbolId": "BONUS", "valueMultiplier": 1},
        {"reel": 2, "row": 0, "symbolId": "BONUS", "valueMultiplier": 1},
    ]
    result = finalize_step_result(
        config=config,
        held_before=held,
        new_symbols=new,
        respins_before=3,
        step_count=0,
        max_steps=500,
        total_bet_minor_units=2000,
        jackpot_tracking=initial_jackpot_tracking(config),
        rng_draw_ids=[],
    )
    assert len(result.frame_local_patch["heldSymbols"]) == 2


def test_finalize_step_result_force_complete_at_max_steps() -> None:
    from runtime_core.plugins.hold_and_win.config import parse_hold_and_win_config
    from runtime_core.plugins.hold_and_win.lifecycle import finalize_step_result
    from runtime_core.plugins.hold_and_win.wins import initial_jackpot_tracking

    config = parse_hold_and_win_config(
        {
            "reelSetId": "hold_and_win",
            "triggerSymbolId": "BONUS",
            "triggerSymbolCount": 1,
            "initialRespins": 3,
            "gridCapacity": 15,
        },
    )
    held = [{"reel": 0, "row": 0, "symbolId": "BONUS", "valueMultiplier": 1}]
    result = finalize_step_result(
        config=config,
        held_before=held,
        new_symbols=[],
        respins_before=3,
        step_count=1,
        max_steps=1,
        total_bet_minor_units=2000,
        jackpot_tracking=initial_jackpot_tracking(config),
        rng_draw_ids=[],
    )
    assert "FEATURE_COMPLETE" in result.trigger_tokens
    assert result.counter_updates[-1].after == 0


def test_resolve_entry_held_symbols_from_existing_state() -> None:
    from runtime_core.common.golden import load_golden_game_version
    from runtime_core.plugins.hold_and_win.config import parse_hold_and_win_config
    from runtime_core.plugins.hold_and_win.lifecycle import build_enter_result, resolve_entry_held_symbols
    from runtime_core.plugins.contracts import PluginContext
    from runtime_core.runtime.frames import new_frame_context

    game = load_golden_game_version("fixture-03-base-hold-win")
    state = game.state_machines["hold_and_win"].states["HAW_RESPINS"]
    frame = new_frame_context()
    frame.frame_local_state["heldSymbols"] = [
        {"reel": 0, "row": 0, "symbolId": "BONUS", "valueMultiplier": 2},
    ] * 6
    ctx = PluginContext(
        plugin_id="core.hold-and-win",
        plugin_version="1.0.0",
        config_schema_version="1.0.0",
        plugin_config=dict(state.plugin_config or {}),
        frame_context=frame,
        rtp_category="HOLD_AND_WIN",
        frame_id="f-1-0",
        machine_id="hold_and_win",
        state_id="HAW_RESPINS",
        plugin_ref_id="haw",
    )
    assert len(resolve_entry_held_symbols(ctx, parse_hold_and_win_config(ctx.plugin_config))) == 6
    build_enter_result(ctx, parse_hold_and_win_config(ctx.plugin_config))


def test_plugin_unknown_reel_set_raises() -> None:
    from runtime_core.common.golden import load_golden_game_version
    from runtime_core.plugins.hold_and_win.plugin import HoldAndWinPlugin

    game = load_golden_game_version("fixture-03-base-hold-win")
    state = game.state_machines["hold_and_win"].states["HAW_RESPINS"]
    frame = new_frame_context()
    frame.frame_local_state["heldSymbols"] = [
        {"reel": 0, "row": 0, "symbolId": "BONUS", "valueMultiplier": 2},
    ] * 6
    frame.respins_remaining = 3
    from runtime_core.plugins.bindings import plugin_game_bindings
    from runtime_core.plugins.contracts import PluginContext

    ctx = PluginContext(
        plugin_id="core.hold-and-win",
        plugin_version="1.0.0",
        config_schema_version="1.0.0",
        plugin_config={
            **dict(state.plugin_config or {}),
            "reelSetId": "missing",
        },
        frame_context=frame,
        rtp_category="HOLD_AND_WIN",
        frame_id="f-1-0",
        machine_id="hold_and_win",
        state_id="HAW_RESPINS",
        plugin_ref_id="haw",
        game_bindings=plugin_game_bindings(game),
    )
    plugin = HoldAndWinPlugin()
    assert plugin.plugin_id == "core.hold-and-win"
    assert plugin.plugin_version == "1.0.0"
    with pytest.raises(PluginConfigurationError, match="unknown reelSetId"):
        plugin.execute_step(ctx, _FixedRNG())
