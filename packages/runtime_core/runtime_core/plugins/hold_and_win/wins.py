"""Hold & Win win and jackpot evaluation."""

from __future__ import annotations

from typing import Any

from runtime_core.plugins.hold_and_win.config import HoldAndWinConfig, qualifying_jackpot_tier
from runtime_core.plugins.hold_and_win.grid import HeldSymbolDict


def evaluate_hold_and_win_wins(
    config: HoldAndWinConfig,
    held_symbols: list[HeldSymbolDict],
    *,
    total_bet_minor_units: int,
    jackpot_tracking: dict[str, bool],
) -> tuple[list[dict[str, Any]], dict[str, bool]]:
    wins: list[dict[str, Any]] = []
    for symbol in held_symbols:
        multiplier = int(symbol.get("valueMultiplier", 1))
        wins.append(
            {
                "source": "hold_and_win",
                "symbolId": str(symbol["symbolId"]),
                "count": 1,
                "winMinorUnits": multiplier * total_bet_minor_units,
                "reel": int(symbol["reel"]),
                "row": int(symbol["row"]),
            },
        )

    updated_tracking = dict(jackpot_tracking)
    tier = qualifying_jackpot_tier(config, len(held_symbols))
    if tier is not None and not updated_tracking.get(tier, False):
        wins.append(
            {
                "source": "jackpot",
                "symbolId": tier,
                "count": len(held_symbols),
                "winMinorUnits": config.jackpot_tiers[tier] * total_bet_minor_units,
            },
        )
        updated_tracking[tier] = True

    return wins, updated_tracking


def initial_jackpot_tracking(config: HoldAndWinConfig) -> dict[str, bool]:
    return {tier: False for tier in config.jackpot_tiers}
