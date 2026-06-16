"""core.multiplier@1.0.0 built-in plugin."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime_core.plugins.contracts import (
    FeaturePlugin,
    FeatureStepResult,
    PluginContext,
)
from runtime_core.plugins.multiplier.apply import apply_multiplier
from runtime_core.plugins.multiplier.config import parse_multiplier_config
from runtime_core.runtime.rng.protocol import RNG

_PENDING_WINS_KEY = "pendingWins"


@dataclass(frozen=True, slots=True)
class MultiplierFactory:
    def create(self) -> FeaturePlugin:
        return MultiplierPlugin()


class MultiplierPlugin:
    """Win multiplier application (fixed and weighted modes)."""

    @property
    def plugin_id(self) -> str:
        return "core.multiplier"

    @property
    def plugin_version(self) -> str:
        return "1.0.0"

    def on_enter(self, ctx: PluginContext) -> None:
        del ctx

    def on_exit(self, ctx: PluginContext) -> None:
        del ctx

    def execute_step(self, ctx: PluginContext, rng: RNG) -> FeatureStepResult:
        pending = ctx.frame_context.frame_local_state.get(_PENDING_WINS_KEY, [])
        wins = [dict(item) for item in pending] if isinstance(pending, list) else []
        return self.apply_wins(ctx.plugin_config, wins, rng)

    def apply_wins(
        self,
        plugin_config: dict[str, Any],
        wins: list[dict[str, Any]],
        rng: RNG,
    ) -> FeatureStepResult:
        config = parse_multiplier_config(plugin_config)
        result = apply_multiplier(config, wins, rng)
        return FeatureStepResult(
            wins=result.wins,
            frame_local_patch={"multiplierFactor": result.factor},
        )
