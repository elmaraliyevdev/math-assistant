"""Theoretical feature trigger frequencies from canonical reel strips."""

from __future__ import annotations

import math
from dataclasses import dataclass

from runtime_core.domain.game_version import GameVersion


@dataclass(frozen=True, slots=True)
class TriggerSpec:
    feature: str
    symbol_id: str
    min_count: int
    reel_set_id: str
    state_id: str


def collect_trigger_specs(game: GameVersion) -> tuple[TriggerSpec, ...]:
    """Extract scatter/bonus trigger rules from main machine states."""
    specs: list[TriggerSpec] = []
    main = game.state_machines.get("main")
    if main is None:
        return ()
    for state_id, state in main.states.items():
        config = state.plugin_config
        reel_set_id = str(config.get("reelSetId", game.game_config.default_reel_set_id))
        for key, emit_field in (
            ("scatterTriggers", "emitTrigger"),
            ("bonusTriggers", "emitTrigger"),
        ):
            raw = config.get(key, [])
            if not isinstance(raw, list):
                continue
            for item in raw:
                if not isinstance(item, dict):
                    continue
                specs.append(
                    TriggerSpec(
                        feature=str(item.get(emit_field, "")),
                        symbol_id=str(item.get("symbolId", "")),
                        min_count=int(item.get("minCount", 0)),
                        reel_set_id=reel_set_id,
                        state_id=state_id,
                    ),
                )
    return tuple(specs)


def probability_reel_shows_symbol(strip: list[str], symbol_id: str, *, window_rows: int) -> float:
    """P(at least one *symbol_id* in a uniformly random stop window)."""
    length = len(strip)
    if length == 0:
        return 0.0
    hits = 0
    for stop in range(length):
        if any(strip[(stop + row) % length] == symbol_id for row in range(window_rows)):
            hits += 1
    return hits / length


def probability_at_least_k_reels(reel_probs: list[float], min_count: int) -> float:
    if min_count <= 0:
        return 1.0
    n = len(reel_probs)
    if n == 0:
        return 0.0

    # DP: prob exactly j reels hit after i reels processed
    dist = [0.0] * (n + 1)
    dist[0] = 1.0
    for prob in reel_probs:
        next_dist = [0.0] * (n + 1)
        for hits, weight in enumerate(dist):
            if weight == 0.0:
                continue
            next_dist[hits] += weight * (1.0 - prob)
            if hits + 1 <= n:
                next_dist[hits + 1] += weight * prob
        dist = next_dist
    return sum(dist[k] for k in range(min_count, n + 1))


def probability_at_least_k_grid_cells(
    strip: list[str],
    symbol_id: str,
    *,
    grid_reels: int,
    grid_rows: int,
    min_count: int,
) -> float:
    """Independent-cell approximation using per-cell symbol density."""
    length = len(strip)
    if length == 0:
        return 0.0
    p_cell = sum(1 for sym in strip if sym == symbol_id) / length
    n_cells = grid_reels * grid_rows
    return sum(
        math.comb(n_cells, k) * (p_cell**k) * ((1.0 - p_cell) ** (n_cells - k))
        for k in range(min_count, n_cells + 1)
    )


def expected_trigger_frequency(game: GameVersion, spec: TriggerSpec) -> float | None:
    """Return expected trigger probability for *spec*, or None if not computable."""
    reel_set = game.reel_sets.get(spec.reel_set_id)
    if reel_set is None or spec.min_count <= 0 or not spec.feature:
        return None

    grid_rows = game.game_config.grid.rows
    grid_reels = game.game_config.grid.reels
    strips = [reel.symbols for reel in sorted(reel_set.reels, key=lambda r: r.reel_index)]
    if len(strips) != grid_reels:
        return None

    reel_probs = [
        probability_reel_shows_symbol(strip, spec.symbol_id, window_rows=grid_rows)
        for strip in strips
    ]

    # When each reel window contains at most one target symbol, reel hit count
    # matches grid symbol count — use the tighter reel model.
    max_per_reel = all(
        sum(1 for sym in strip if sym == spec.symbol_id) <= 1 for strip in strips
    )
    if max_per_reel:
        return probability_at_least_k_reels(reel_probs, spec.min_count)

    return probability_at_least_k_grid_cells(
        strips[0],
        spec.symbol_id,
        grid_reels=grid_reels,
        grid_rows=grid_rows,
        min_count=spec.min_count,
    )


def expected_feature_frequencies(game: GameVersion) -> dict[str, float]:
    """Map feature trigger name to theoretical frequency (0..1 ratio)."""
    frequencies: dict[str, float] = {}
    for spec in collect_trigger_specs(game):
        if spec.state_id != "BASE":
            continue
        expected = expected_trigger_frequency(game, spec)
        if expected is None:
            continue
        # Keep the highest-probability entry per feature name on BASE.
        current = frequencies.get(spec.feature)
        if current is None or expected > current:
            frequencies[spec.feature] = expected
    return frequencies
