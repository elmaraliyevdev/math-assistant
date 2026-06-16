"""Shared base-game spin execution for grid generation and win evaluation."""

from __future__ import annotations

from typing import Any

from runtime_core.plugins.base_game.grid import generate_grid
from runtime_core.plugins.base_game.lines import evaluate_line_wins
from runtime_core.plugins.base_game.scatter import (
    SymbolTriggerRule,
    build_entry_held_symbols,
    build_scatter_counts,
    count_symbol_on_grid,
    evaluate_trigger_tokens,
    parse_symbol_triggers,
)
from runtime_core.plugins.bindings import PluginGameBindings
from runtime_core.plugins.contracts import FeatureStepResult
from runtime_core.plugins.exceptions import PluginConfigurationError
from runtime_core.runtime.rng.protocol import RNG


def execute_base_spin(
    bindings: PluginGameBindings,
    *,
    reel_set_id: str,
    rng: RNG,
    scatter_rules: tuple[SymbolTriggerRule, ...] = (),
    bonus_rules: tuple[SymbolTriggerRule, ...] = (),
    include_spin_complete_fallback: bool = True,
) -> FeatureStepResult:
    """Run one deterministic grid spin with line evaluation and optional triggers."""
    reel_set = bindings.reel_sets.get(reel_set_id)
    if reel_set is None:
        msg = f"unknown reelSetId {reel_set_id!r}"
        raise PluginConfigurationError(msg)

    grid = generate_grid(
        reel_set,
        grid_reels=bindings.grid_reels,
        grid_rows=bindings.grid_rows,
        rng=rng,
    )
    wins = evaluate_line_wins(
        grid.symbols,
        bindings.paytable,
        bindings.win_model,
        bindings.bet_per_line_minor_units,
    )
    scatter_counts = build_scatter_counts(
        grid.symbols,
        scatter_rules + bonus_rules,
    )
    held_symbols: list[dict[str, int | str]] = []
    seen_symbols: set[str] = set()
    for rule in bonus_rules:
        if rule.symbol_id not in seen_symbols:
            held_symbols.extend(
                build_entry_held_symbols(grid.symbols, rule.symbol_id),
            )
            seen_symbols.add(rule.symbol_id)
    if include_spin_complete_fallback:
        trigger_tokens = evaluate_trigger_tokens(
            grid.symbols,
            scatter_rules,
            bonus_rules,
        )
    else:
        trigger_tokens = _feature_trigger_tokens(
            grid.symbols,
            scatter_rules,
            bonus_rules,
        )
    return FeatureStepResult(
        trigger_tokens=trigger_tokens,
        wins=wins,
        grid_outcome=_grid_outcome(grid.reel_set_id, grid.symbols, grid.rng_draw_ids),
        frame_local_patch={
            "scatterCounts": scatter_counts,
            "entryHeldSymbols": held_symbols,
        },
    )


def parse_spin_config(config: dict[str, object]) -> tuple[str, tuple[SymbolTriggerRule, ...], tuple[SymbolTriggerRule, ...]]:
    reel_set_id = str(config["reelSetId"])
    scatter_raw = config.get("scatterTriggers", [])
    bonus_raw = config.get("bonusTriggers", [])
    scatter_rules = parse_symbol_triggers(
        scatter_raw if isinstance(scatter_raw, list) else [],
    )
    bonus_rules = parse_symbol_triggers(
        bonus_raw if isinstance(bonus_raw, list) else [],
    )
    return reel_set_id, scatter_rules, bonus_rules


def _feature_trigger_tokens(
    symbols: list[list[str]],
    scatter_rules: tuple[SymbolTriggerRule, ...],
    bonus_rules: tuple[SymbolTriggerRule, ...],
) -> list[str]:
    tokens: list[str] = []
    for rule in scatter_rules:
        if count_symbol_on_grid(symbols, rule.symbol_id) >= rule.min_count:
            tokens.append(rule.emit_trigger)
    for rule in bonus_rules:
        if count_symbol_on_grid(symbols, rule.symbol_id) >= rule.min_count:
            tokens.append(rule.emit_trigger)
    return tokens


def _grid_outcome(
    reel_set_id: str,
    symbols: list[list[str]],
    rng_draw_ids: list[int],
) -> dict[str, Any]:
    return {
        "reelSetId": reel_set_id,
        "symbols": symbols,
        "rngDrawIds": rng_draw_ids,
    }
