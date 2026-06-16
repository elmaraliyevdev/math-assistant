"""core.hold-and-win@1.0.0 built-in plugin."""

from __future__ import annotations

from dataclasses import dataclass, field

from runtime_core.plugins.contracts import (
    FeaturePlugin,
    FeatureStepResult,
    PluginContext,
)
from runtime_core.plugins.exceptions import PluginConfigurationError
from runtime_core.plugins.hold_and_win.config import parse_hold_and_win_config
from runtime_core.plugins.hold_and_win.grid import generate_respin_lands, normalize_held_symbols
from runtime_core.plugins.hold_and_win.lifecycle import build_enter_result, finalize_step_result
from runtime_core.runtime.rng.protocol import RNG

_HELD_SYMBOLS_KEY = "heldSymbols"
_JACKPOT_TRACKING_KEY = "jackpotTracking"
_HAW_STEP_COUNT_KEY = "hawStepCount"


@dataclass
class HoldAndWinPlugin:
    """Hold & Win respin feature plugin."""

    _enter_result: FeatureStepResult | None = field(default=None, repr=False)

    @property
    def plugin_id(self) -> str:
        return "core.hold-and-win"

    @property
    def plugin_version(self) -> str:
        return "1.0.0"

    def on_enter(self, ctx: PluginContext) -> None:
        config = parse_hold_and_win_config(ctx.plugin_config)
        self._enter_result = build_enter_result(ctx, config)

    def enter_result(self) -> FeatureStepResult | None:
        result, self._enter_result = self._enter_result, None
        return result

    def on_exit(self, ctx: PluginContext) -> None:
        del ctx

    def execute_step(self, ctx: PluginContext, rng: RNG) -> FeatureStepResult:
        bindings = ctx.game_bindings
        if bindings is None:
            msg = "core.hold-and-win requires PluginContext.game_bindings"
            raise PluginConfigurationError(msg)

        config = parse_hold_and_win_config(ctx.plugin_config)
        reel_set = bindings.reel_sets.get(config.reel_set_id)
        if reel_set is None:
            msg = f"unknown reelSetId {config.reel_set_id!r}"
            raise PluginConfigurationError(msg)

        state = ctx.frame_context.frame_local_state
        held_before = normalize_held_symbols(
            state.get(_HELD_SYMBOLS_KEY, [])
            if isinstance(state.get(_HELD_SYMBOLS_KEY), list)
            else [],
        )
        jackpot_tracking = (
            dict(state[_JACKPOT_TRACKING_KEY])
            if isinstance(state.get(_JACKPOT_TRACKING_KEY), dict)
            else {}
        )
        step_count = int(state.get(_HAW_STEP_COUNT_KEY, 0))

        respin = generate_respin_lands(
            config,
            reel_set,
            grid_reels=bindings.grid_reels,
            grid_rows=bindings.grid_rows,
            held_symbols=held_before,
            rng=rng,
        )
        return finalize_step_result(
            config=config,
            held_before=held_before,
            new_symbols=respin.new_symbols,
            respins_before=ctx.frame_context.respins_remaining,
            step_count=step_count,
            max_steps=bindings.max_steps_per_spin_chain,
            total_bet_minor_units=bindings.total_bet_minor_units,
            jackpot_tracking=jackpot_tracking,
            rng_draw_ids=respin.rng_draw_ids,
        )


@dataclass(frozen=True, slots=True)
class HoldAndWinFactory:
    def create(self) -> FeaturePlugin:
        return HoldAndWinPlugin()
