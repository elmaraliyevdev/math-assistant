"""core.free-spins@1.0.0 built-in plugin."""

from __future__ import annotations

from dataclasses import dataclass, field

from runtime_core.plugins.base_game.spin import execute_base_spin, parse_spin_config
from runtime_core.plugins.contracts import (
    FeaturePlugin,
    FeatureStepResult,
    PluginContext,
)
from runtime_core.plugins.exceptions import PluginConfigurationError
from runtime_core.plugins.free_spins.config import parse_free_spins_config
from runtime_core.plugins.free_spins.lifecycle import (
    build_enter_result,
    finalize_step_result,
)
from runtime_core.plugins.free_spins.retrigger import evaluate_retrigger
from runtime_core.runtime.rng.protocol import RNG


@dataclass
class FreeSpinsPlugin:
    """Free Spins feature plugin composing base-game spin execution."""

    _enter_result: FeatureStepResult | None = field(default=None, repr=False)

    @property
    def plugin_id(self) -> str:
        return "core.free-spins"

    @property
    def plugin_version(self) -> str:
        return "1.0.0"

    def on_enter(self, ctx: PluginContext) -> None:
        config = parse_free_spins_config(ctx.plugin_config)
        self._enter_result = build_enter_result(ctx, config)

    def enter_result(self) -> FeatureStepResult | None:
        result, self._enter_result = self._enter_result, None
        return result

    def on_exit(self, ctx: PluginContext) -> None:
        del ctx

    def execute_step(self, ctx: PluginContext, rng: RNG) -> FeatureStepResult:
        bindings = ctx.game_bindings
        if bindings is None:
            msg = "core.free-spins requires PluginContext.game_bindings"
            raise PluginConfigurationError(msg)

        config = parse_free_spins_config(ctx.plugin_config)
        _, _scatter_rules, bonus_rules = parse_spin_config(ctx.plugin_config)
        spin_result = execute_base_spin(
            bindings,
            reel_set_id=config.reel_set_id,
            rng=rng,
            scatter_rules=(),
            bonus_rules=bonus_rules,
            include_spin_complete_fallback=False,
        )

        scatter_counts = spin_result.frame_local_patch.get("scatterCounts", {})
        scatter_count = 0
        if isinstance(scatter_counts, dict):
            scatter_count = int(scatter_counts.get("SCATTER", 0))

        retrigger_count = int(
            ctx.frame_context.frame_local_state.get("fsRetriggerCount", 0),
        )
        step_count = int(ctx.frame_context.frame_local_state.get("fsStepCount", 0))
        retrigger = evaluate_retrigger(
            config,
            bindings,
            scatter_count=scatter_count,
            current_retrigger_count=retrigger_count,
        )
        return finalize_step_result(
            spin_result,
            spins_before=ctx.frame_context.spins_remaining,
            retrigger=retrigger,
            max_steps=bindings.max_steps_per_spin_chain,
            current_step_count=step_count,
        )


@dataclass(frozen=True, slots=True)
class FreeSpinsFactory:
    def create(self) -> FeaturePlugin:
        return FreeSpinsPlugin()
