"""Immutable game snapshot bindings for built-in plugin execution."""

from __future__ import annotations

from dataclasses import dataclass

from runtime_core.domain.game_version import GameVersion
from runtime_core.domain.plugins import Paytable, ReelSet, WinModel
from runtime_core.runtime.session.resolution import resolve_bet


@dataclass(frozen=True, slots=True)
class PluginGameBindings:
    """Read-only game mathematics snapshot required by spin plugins."""

    grid_reels: int
    grid_rows: int
    reel_sets: dict[str, ReelSet]
    paytable: Paytable
    win_model: WinModel
    bet_per_line_minor_units: int
    total_bet_minor_units: int
    max_retriggers_per_feature: int | None = None
    max_steps_per_spin_chain: int | None = None


def plugin_game_bindings(
    game: GameVersion,
    *,
    total_bet_minor_units: int | None = None,
) -> PluginGameBindings:
    """Build plugin bindings from a validated ``GameVersion`` snapshot."""
    if total_bet_minor_units is not None and total_bet_minor_units > 0:
        total_bet = total_bet_minor_units
    else:
        _, total_bet = resolve_bet(game, 0)
    lines = game.bet_model.line_count or 0
    if lines <= 0:
        lines = 1
    bet_per_line = total_bet // lines
    grid = game.game_config.grid
    limits = game.session.runtime_limits
    max_retriggers = limits.max_respins_per_feature if limits else None
    max_steps = limits.max_steps_per_spin_chain if limits else None
    return PluginGameBindings(
        grid_reels=grid.reels,
        grid_rows=grid.rows,
        reel_sets=dict(game.reel_sets),
        paytable=game.paytable,
        win_model=game.win_model,
        bet_per_line_minor_units=bet_per_line,
        total_bet_minor_units=total_bet,
        max_retriggers_per_feature=max_retriggers,
        max_steps_per_spin_chain=max_steps,
    )
