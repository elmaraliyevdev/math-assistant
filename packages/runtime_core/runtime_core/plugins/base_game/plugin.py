"""core.base-game@1.0.0 built-in plugin."""

from __future__ import annotations

from dataclasses import dataclass

from runtime_core.plugins.base_game.spin import execute_base_spin, parse_spin_config
from runtime_core.plugins.contracts import (
    FeaturePlugin,
    FeatureStepResult,
    PluginContext,
)
from runtime_core.plugins.exceptions import PluginConfigurationError
from runtime_core.runtime.rng.protocol import RNG


@dataclass(frozen=True, slots=True)
class BaseGameFactory:
    def create(self) -> FeaturePlugin:
        return BaseGamePlugin()


class BaseGamePlugin:
    """Base grid spin, line wins, scatter triggers (§12.5)."""

    @property
    def plugin_id(self) -> str:
        return "core.base-game"

    @property
    def plugin_version(self) -> str:
        return "1.0.0"

    def on_enter(self, ctx: PluginContext) -> None:
        del ctx

    def on_exit(self, ctx: PluginContext) -> None:
        del ctx

    def execute_step(self, ctx: PluginContext, rng: RNG) -> FeatureStepResult:
        bindings = ctx.game_bindings
        if bindings is None:
            msg = "core.base-game requires PluginContext.game_bindings"
            raise PluginConfigurationError(msg)
        reel_set_id, scatter_rules, bonus_rules = parse_spin_config(ctx.plugin_config)
        return execute_base_spin(
            bindings,
            reel_set_id=reel_set_id,
            rng=rng,
            scatter_rules=scatter_rules,
            bonus_rules=bonus_rules,
            include_spin_complete_fallback=True,
        )
