"""Scatter and bonus trigger evaluation for core.base-game."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SymbolTriggerRule:
    symbol_id: str
    min_count: int
    emit_trigger: str


def parse_symbol_triggers(raw: list[dict[str, object]]) -> tuple[SymbolTriggerRule, ...]:
    rules: list[SymbolTriggerRule] = []
    for item in raw:
        rules.append(
            SymbolTriggerRule(
                symbol_id=str(item["symbolId"]),
                min_count=int(item["minCount"]),  # type: ignore[arg-type]
                emit_trigger=str(item["emitTrigger"]),
            ),
        )
    return tuple(rules)


def count_symbol_on_grid(symbols: list[list[str]], symbol_id: str) -> int:
    return sum(1 for row in symbols for cell in row if cell == symbol_id)


def build_scatter_counts(
    symbols: list[list[str]],
    rules: tuple[SymbolTriggerRule, ...],
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for rule in rules:
        count = count_symbol_on_grid(symbols, rule.symbol_id)
        if count > 0:
            counts[rule.symbol_id] = count
    return counts


def build_entry_held_symbols(
    symbols: list[list[str]],
    symbol_id: str,
) -> list[dict[str, int | str]]:
    held: list[dict[str, int | str]] = []
    for row_idx, row in enumerate(symbols):
        for reel_idx, cell in enumerate(row):
            if cell == symbol_id:
                held.append(
                    {"reel": reel_idx, "row": row_idx, "symbolId": symbol_id},
                )
    return held


def evaluate_trigger_tokens(
    symbols: list[list[str]],
    scatter_rules: tuple[SymbolTriggerRule, ...],
    bonus_rules: tuple[SymbolTriggerRule, ...],
) -> list[str]:
    """Emit feature trigger tokens; otherwise emit ``SPIN_COMPLETE``."""
    tokens: list[str] = []
    for rule in scatter_rules:
        if count_symbol_on_grid(symbols, rule.symbol_id) >= rule.min_count:
            tokens.append(rule.emit_trigger)
    for rule in bonus_rules:
        if count_symbol_on_grid(symbols, rule.symbol_id) >= rule.min_count:
            tokens.append(rule.emit_trigger)
    if tokens:
        return tokens
    return ["SPIN_COMPLETE"]
