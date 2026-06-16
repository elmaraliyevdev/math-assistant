"""Hold & Win plugin configuration parsing."""

from __future__ import annotations

from dataclasses import dataclass

from runtime_core.plugins.exceptions import PluginConfigurationError

_JACKPOT_TIER_ORDER = ("grand", "major", "minor", "mini")
_JACKPOT_THRESHOLDS = {
    "grand": 1.0,
    "major": 0.93,
    "minor": 0.8,
    "mini": 0.67,
}


@dataclass(frozen=True, slots=True)
class HoldAndWinConfig:
    reel_set_id: str
    trigger_symbol_id: str
    trigger_symbol_count: int
    initial_respins: int
    grid_capacity: int
    symbol_values: dict[str, int]
    jackpot_tiers: dict[str, int]
    fill_ends_feature: bool = True


def parse_hold_and_win_config(raw: dict[str, object]) -> HoldAndWinConfig:
    symbol_values_raw = raw.get("symbolValues", {})
    jackpot_raw = raw.get("jackpotTiers", {})
    symbol_values = (
        {str(k): int(v) for k, v in symbol_values_raw.items()}  # type: ignore[union-attr]
        if isinstance(symbol_values_raw, dict)
        else {}
    )
    jackpot_tiers = (
        {str(k): int(v) for k, v in jackpot_raw.items()}  # type: ignore[union-attr]
        if isinstance(jackpot_raw, dict)
        else {}
    )
    fill_ends = raw.get("fillEndsFeature", True)
    return HoldAndWinConfig(
        reel_set_id=str(raw["reelSetId"]),
        trigger_symbol_id=str(raw["triggerSymbolId"]),
        trigger_symbol_count=int(raw["triggerSymbolCount"]),  # type: ignore[arg-type]
        initial_respins=int(raw["initialRespins"]),  # type: ignore[arg-type]
        grid_capacity=int(raw["gridCapacity"]),  # type: ignore[arg-type]
        symbol_values=symbol_values,
        jackpot_tiers=jackpot_tiers,
        fill_ends_feature=bool(fill_ends),
    )


def jackpot_threshold(config: HoldAndWinConfig, tier: str) -> int:
    ratio = _JACKPOT_THRESHOLDS.get(tier)
    if ratio is None:
        msg = f"unknown jackpot tier {tier!r}"
        raise PluginConfigurationError(msg)
    minimum = int(ratio * config.grid_capacity)
    if ratio >= 1.0:
        return config.grid_capacity
    return max(minimum, 1)


def qualifying_jackpot_tier(
    config: HoldAndWinConfig,
    held_count: int,
) -> str | None:
    for tier in _JACKPOT_TIER_ORDER:
        if tier not in config.jackpot_tiers:
            continue
        if held_count >= jackpot_threshold(config, tier):
            return tier
    return None
