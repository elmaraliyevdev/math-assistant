"""Hold grid respin generation for core.hold-and-win."""

from __future__ import annotations

from dataclasses import dataclass

from runtime_core.domain.plugins import ReelSet
from runtime_core.plugins.hold_and_win.config import HoldAndWinConfig
from runtime_core.runtime.rng.protocol import RNG

HeldSymbolDict = dict[str, int | str]


@dataclass(frozen=True, slots=True)
class RespinOutcome:
    new_symbols: list[HeldSymbolDict]
    rng_draw_ids: list[int]


def held_position_key(symbol: HeldSymbolDict) -> tuple[int, int]:
    return int(symbol["reel"]), int(symbol["row"])


def normalize_held_symbols(raw: list[object]) -> list[HeldSymbolDict]:
    held: list[HeldSymbolDict] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        held.append(
            {
                "reel": int(item["reel"]),
                "row": int(item["row"]),
                "symbolId": str(item["symbolId"]),
                "valueMultiplier": int(item.get("valueMultiplier", 1)),
            },
        )
    return held


def generate_respin_lands(
    config: HoldAndWinConfig,
    reel_set: ReelSet,
    *,
    grid_reels: int,
    grid_rows: int,
    held_symbols: list[HeldSymbolDict],
    rng: RNG,
) -> RespinOutcome:
    occupied = {held_position_key(symbol) for symbol in held_symbols}
    reels = sorted(reel_set.reels, key=lambda reel: reel.reel_index)
    new_symbols: list[HeldSymbolDict] = []
    draw_ids: list[int] = []

    if len(held_symbols) >= config.grid_capacity:
        return RespinOutcome(new_symbols=new_symbols, rng_draw_ids=draw_ids)

    for row in range(grid_rows):
        for reel_index in range(grid_reels):
            if (reel_index, row) in occupied:
                continue
            if len(held_symbols) + len(new_symbols) >= config.grid_capacity:
                break
            strip = reels[reel_index].symbols
            stop = rng.next_int(len(strip))
            draw_ids.append(rng.draw_id)
            symbol = strip[(stop + row) % len(strip)]
            if symbol != config.trigger_symbol_id:
                continue
            multiplier = config.symbol_values.get(symbol, 1)
            new_symbols.append(
                {
                    "reel": reel_index,
                    "row": row,
                    "symbolId": symbol,
                    "valueMultiplier": multiplier,
                },
            )
            occupied.add((reel_index, row))

    return RespinOutcome(new_symbols=new_symbols, rng_draw_ids=draw_ids)
