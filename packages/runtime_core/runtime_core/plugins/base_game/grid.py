"""Reel stop and symbol grid generation for core.base-game."""

from __future__ import annotations

from dataclasses import dataclass

from runtime_core.domain.plugins import ReelSet
from runtime_core.runtime.rng.protocol import RNG


@dataclass(frozen=True, slots=True)
class GridGenerationResult:
    """Deterministic grid outcome from reel stops."""

    reel_set_id: str
    symbols: list[list[str]]
    stops: list[int]
    rng_draw_ids: list[int]


def generate_grid(
    reel_set: ReelSet,
    *,
    grid_reels: int,
    grid_rows: int,
    rng: RNG,
) -> GridGenerationResult:
    """Pick reel stops and build a row-major symbol grid."""
    stops: list[int] = []
    draw_ids: list[int] = []
    columns: list[list[str]] = []

    reels = sorted(reel_set.reels, key=lambda reel: reel.reel_index)
    if len(reels) != grid_reels:
        msg = (
            f"reel set {reel_set.id!r} has {len(reels)} reels, "
            f"expected {grid_reels}"
        )
        raise ValueError(msg)

    for reel in reels:
        strip = reel.symbols
        if not strip:
            msg = f"reel {reel.reel_index} in set {reel_set.id!r} is empty"
            raise ValueError(msg)
        stop = rng.next_int(len(strip))
        stops.append(stop)
        draw_ids.append(rng.draw_id)
        column = [strip[(stop + row) % len(strip)] for row in range(grid_rows)]
        columns.append(column)

    rows = [
        [columns[reel][row] for reel in range(grid_reels)]
        for row in range(grid_rows)
    ]
    return GridGenerationResult(
        reel_set_id=reel_set.id,
        symbols=rows,
        stops=stops,
        rng_draw_ids=draw_ids,
    )
