"""Exact theoretical RTP from reel-strip enumeration."""

from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

from runtime_core.domain.game_version import GameVersion
from runtime_core.domain.plugins import PaytableEntry, ReelSet, ReelStrip
from runtime_core.plugins.bindings import plugin_game_bindings
from runtime_core.theoretical.models import TheoreticalRtpResult

if TYPE_CHECKING:
    from collections.abc import Iterator

_MAX_OUTCOMES = 10_000_000


def calculate_theoretical_rtp(
    game: GameVersion,
    *,
    reel_set_id: str | None = None,
    total_bet_minor_units: int | None = None,
) -> TheoreticalRtpResult:
    """Enumerate reel stops and compute exact base-game RTP."""
    if game.win_model.type != "lines":
        msg = f"unsupported win model type {game.win_model.type!r}"
        raise ValueError(msg)

    bindings = plugin_game_bindings(
        game,
        total_bet_minor_units=total_bet_minor_units,
    )
    resolved_reel_set_id = reel_set_id or game.game_config.default_reel_set_id
    reel_set = bindings.reel_sets.get(resolved_reel_set_id)
    if reel_set is None:
        msg = f"reel set {resolved_reel_set_id!r} not found"
        raise ValueError(msg)

    strips = _sorted_strips(reel_set, bindings.grid_reels)
    outcome_count = _outcome_count(strips)
    if outcome_count > _MAX_OUTCOMES:
        msg = (
            f"reel strip enumeration exceeds {_MAX_OUTCOMES} outcomes "
            f"({outcome_count}); reduce strip lengths or reel count"
        )
        raise ValueError(msg)

    pays_by_symbol = _group_paytable(bindings.paytable.pays)
    scatter_paying = _scatter_paying_symbols(game)
    wild_ids, wild_substitutes = _wild_configuration(game)
    highest_only = bindings.win_model.highest_win_only_per_line is not False

    line_ev = 0.0
    scatter_ev = 0.0
    for combo, probability in _enumerate_outcomes(strips):
        grid = _grid_from_stops(strips, combo, bindings.grid_rows)
        line_ev += (
            _evaluate_line_wins(
                grid,
                bindings.paytable.lines or [],
                pays_by_symbol,
                bindings.bet_per_line_minor_units,
                wild_ids=wild_ids,
                wild_substitutes=wild_substitutes,
                highest_only=highest_only,
            )
            * probability
        )
        scatter_ev += (
            _evaluate_scatter_pays(
                grid,
                pays_by_symbol,
                scatter_paying,
                bindings.total_bet_minor_units,
            )
            * probability
        )

    total_bet = bindings.total_bet_minor_units
    line_rtp = line_ev / total_bet if total_bet > 0 else 0.0
    scatter_rtp = scatter_ev / total_bet if total_bet > 0 else 0.0
    base_rtp = line_rtp + scatter_rtp

    return TheoreticalRtpResult(
        totalRtp=base_rtp,
        baseRtp=base_rtp,
        scatterRtp=scatter_rtp,
        lineRtp=line_rtp,
        outcomeCount=outcome_count,
        reelSetId=resolved_reel_set_id,
    )


def _sorted_strips(reel_set: ReelSet, grid_reels: int) -> list[ReelStrip]:
    reels = sorted(reel_set.reels, key=lambda reel: reel.reel_index)
    if len(reels) != grid_reels:
        msg = (
            f"reel set {reel_set.id!r} has {len(reels)} reels, "
            f"expected {grid_reels}"
        )
        raise ValueError(msg)
    for reel in reels:
        if not reel.symbols:
            msg = f"reel {reel.reel_index} in set {reel_set.id!r} is empty"
            raise ValueError(msg)
    return reels


def _outcome_count(strips: list[ReelStrip]) -> int:
    count = 1
    for strip in strips:
        count *= len(strip.symbols)
    return count


def _stop_probabilities(strip: ReelStrip) -> list[float]:
    weights = strip.weights
    symbols = strip.symbols
    if weights is not None and len(weights) == len(symbols):
        total = float(sum(weights))
        if total <= 0:
            msg = f"reel {strip.reel_index} has non-positive weight sum"
            raise ValueError(msg)
        return [weight / total for weight in weights]
    uniform = 1.0 / len(symbols)
    return [uniform] * len(symbols)


def _enumerate_outcomes(
    strips: list[ReelStrip],
) -> Iterator[tuple[tuple[int, ...], float]]:
    stop_ranges = [range(len(strip.symbols)) for strip in strips]
    per_reel_probs = [_stop_probabilities(strip) for strip in strips]
    for combo in itertools.product(*stop_ranges):
        probability = 1.0
        for reel_index, stop in enumerate(combo):
            probability *= per_reel_probs[reel_index][stop]
        yield combo, probability


def _grid_from_stops(
    strips: list[ReelStrip],
    stops: tuple[int, ...],
    grid_rows: int,
) -> list[list[str]]:
    columns: list[list[str]] = []
    for strip, stop in zip(strips, stops, strict=True):
        length = len(strip.symbols)
        column = [strip.symbols[(stop + row) % length] for row in range(grid_rows)]
        columns.append(column)
    return [
        [columns[reel][row] for reel in range(len(columns))]
        for row in range(grid_rows)
    ]


def _group_paytable(
    pays: list[PaytableEntry],
) -> dict[str, list[PaytableEntry]]:
    grouped: dict[str, list[PaytableEntry]] = {}
    for entry in pays:
        grouped.setdefault(entry.symbol_id, []).append(entry)
    for entries in grouped.values():
        entries.sort(key=lambda item: item.count)
    return grouped


def _scatter_paying_symbols(game: GameVersion) -> set[str]:
    paying: set[str] = set()
    for symbol_id, meta in game.symbols.items():
        if meta.get("type") != "scatter":
            continue
        if meta.get("pays") is False:
            continue
        paying.add(symbol_id)
    return paying


def _wild_configuration(
    game: GameVersion,
) -> tuple[frozenset[str], dict[str, frozenset[str]]]:
    paying_symbols = frozenset(
        symbol_id
        for symbol_id, meta in game.symbols.items()
        if meta.get("type") not in ("scatter", "bonus", "wild")
    )
    wild_ids: set[str] = set()
    wild_substitutes: dict[str, frozenset[str]] = {}
    for symbol_id, meta in game.symbols.items():
        if meta.get("type") != "wild":
            continue
        wild_ids.add(symbol_id)
        substitutes = meta.get("substitutes")
        if isinstance(substitutes, list):
            wild_substitutes[symbol_id] = frozenset(str(item) for item in substitutes)
        elif meta.get("substituteAllPaying"):
            wild_substitutes[symbol_id] = paying_symbols
        else:
            wild_substitutes[symbol_id] = paying_symbols
    return frozenset(wild_ids), wild_substitutes


def _evaluate_line_wins(
    symbols: list[list[str]],
    lines: list,
    pays_by_symbol: dict[str, list[PaytableEntry]],
    bet_per_line_minor_units: int,
    *,
    wild_ids: frozenset[str],
    wild_substitutes: dict[str, frozenset[str]],
    highest_only: bool,
) -> int:
    total = 0
    for line in lines:
        line_symbols = [
            symbols[row][reel]
            for reel, row in enumerate(line.path)
            if row < len(symbols) and reel < len(symbols[row])
        ]
        if not line_symbols:
            continue
        win = _best_line_win(
            line_symbols,
            pays_by_symbol,
            bet_per_line_minor_units,
            wild_ids=wild_ids,
            wild_substitutes=wild_substitutes,
            highest_only=highest_only,
        )
        total += win
    return total


def _best_line_win(
    line_symbols: list[str],
    pays_by_symbol: dict[str, list[PaytableEntry]],
    bet_per_line_minor_units: int,
    *,
    wild_ids: frozenset[str],
    wild_substitutes: dict[str, frozenset[str]],
    highest_only: bool,
) -> int:
    candidates = set(pays_by_symbol)
    best_win = 0
    for symbol_id in candidates:
        count = _consecutive_matches(
            line_symbols,
            symbol_id,
            wild_ids=wild_ids,
            wild_substitutes=wild_substitutes,
        )
        entries = pays_by_symbol.get(symbol_id, [])
        entry = _qualifying_entry(entries, count)
        if entry is None:
            continue
        win = _pay_multiplier(entry.multiplier) * bet_per_line_minor_units
        if highest_only:
            best_win = max(best_win, win)
        else:
            best_win += win
    return best_win


def _consecutive_matches(
    line_symbols: list[str],
    target_symbol: str,
    *,
    wild_ids: frozenset[str],
    wild_substitutes: dict[str, frozenset[str]],
) -> int:
    count = 0
    for symbol in line_symbols:
        if symbol == target_symbol:
            count += 1
        elif symbol in wild_ids and target_symbol in wild_substitutes.get(symbol, ()):
            count += 1
        else:
            break
    return count


def _qualifying_entry(
    entries: list[PaytableEntry],
    count: int,
) -> PaytableEntry | None:
    best: PaytableEntry | None = None
    for entry in entries:
        if entry.count <= count and (best is None or entry.count > best.count):
            best = entry
    return best


def _evaluate_scatter_pays(
    symbols: list[list[str]],
    pays_by_symbol: dict[str, list[PaytableEntry]],
    scatter_paying: set[str],
    total_bet_minor_units: int,
) -> int:
    if not scatter_paying:
        return 0
    flat = [cell for row in symbols for cell in row]
    total = 0
    for symbol_id in scatter_paying:
        count = flat.count(symbol_id)
        if count <= 0:
            continue
        entries = pays_by_symbol.get(symbol_id, [])
        entry = _qualifying_entry(entries, count)
        if entry is None:
            continue
        total += _pay_multiplier(entry.multiplier) * total_bet_minor_units
    return total


def _pay_multiplier(value: int | float) -> int:
    if isinstance(value, float):
        return int(round(value))
    return int(value)
