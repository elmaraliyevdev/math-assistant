"""Payline evaluation for core.base-game."""

from __future__ import annotations

from runtime_core.domain.plugins import Paytable, PaytableEntry, WinModel


def evaluate_line_wins(
    symbols: list[list[str]],
    paytable: Paytable,
    win_model: WinModel,
    bet_per_line_minor_units: int,
) -> list[dict[str, int | str]]:
    """Evaluate configured paylines and return WinComponent-compatible dicts."""
    if win_model.type != "lines":
        return []
    lines = paytable.lines or []
    if not lines:
        return []

    pays_by_symbol: dict[str, list[PaytableEntry]] = {}
    for entry in paytable.pays:
        pays_by_symbol.setdefault(entry.symbol_id, []).append(entry)
    for entries in pays_by_symbol.values():
        entries.sort(key=lambda item: item.count)

    wins: list[dict[str, int | str]] = []
    for line in lines:
        line_symbols = [
            symbols[row][reel]
            for reel, row in enumerate(line.path)
            if row < len(symbols) and reel < len(symbols[row])
        ]
        if not line_symbols:
            continue
        component = _best_line_win(
            line_symbols,
            line.index,
            pays_by_symbol,
            bet_per_line_minor_units,
            highest_only=win_model.highest_win_only_per_line is not False,
        )
        if component is not None:
            wins.append(component)
    return wins


def _best_line_win(
    line_symbols: list[str],
    line_index: int,
    pays_by_symbol: dict[str, list[PaytableEntry]],
    bet_per_line_minor_units: int,
    *,
    highest_only: bool,
) -> dict[str, int | str] | None:
    lead = line_symbols[0]
    count = 1
    for symbol in line_symbols[1:]:
        if symbol != lead:
            break
        count += 1

    entries = pays_by_symbol.get(lead, [])
    best: PaytableEntry | None = None
    for entry in entries:
        if entry.count <= count and (best is None or entry.count > best.count):
            best = entry

    if best is None:
        return None

    multiplier = _pay_multiplier(best.multiplier)
    win_minor = multiplier * bet_per_line_minor_units
    return {
        "source": "lines",
        "symbolId": best.symbol_id,
        "count": best.count,
        "winMinorUnits": win_minor,
        "lineIndex": line_index,
    }


def _pay_multiplier(value: int | float) -> int:
    if isinstance(value, float):
        return int(round(value))
    return int(value)
