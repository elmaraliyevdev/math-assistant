"""Exposure cap validation (strict mode)."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.validation.issues import (
    graph_exposure_cap_exceeded,
    graph_exposure_cap_invalid,
    graph_exposure_multiplier_invalid,
    graph_exposure_scope_invalid,
)
from runtime_core.validation.report import ValidationReport

_VALID_CAP_SCOPES = frozenset({"session_spin_chain", "single_spin", "feature"})


class ExposureValidator:
    def validate(self, game: GameVersion | None) -> ValidationReport:
        report = ValidationReport.empty()
        if game is None:
            return report
        exposure = game.exposure
        if exposure.validation_mode != "strict":
            return report
        if exposure.enforce_cap and exposure.max_win_minor_units <= 0:
            report.add_error(graph_exposure_cap_invalid())
        if exposure.enforce_cap and (exposure.max_win_multiplier or 0) <= 0:
            report.add_error(graph_exposure_multiplier_invalid())
        if exposure.cap_scope not in _VALID_CAP_SCOPES:
            report.add_error(graph_exposure_scope_invalid(exposure.cap_scope))
        if not exposure.enforce_cap:
            return report
        theoretical = _theoretical_max_win_minor(game)
        effective_cap = _effective_exposure_cap(game)
        if effective_cap > 0 and theoretical > effective_cap:
            report.add_error(graph_exposure_cap_exceeded(theoretical, effective_cap))
        return report


def _effective_exposure_cap(game: GameVersion) -> int:
    exposure = game.exposure
    cap = exposure.max_win_minor_units
    total_bet = _total_bet_minor(game)
    multiplier = exposure.max_win_multiplier or 0
    if multiplier > 0 and total_bet > 0:
        mult_cap = multiplier * total_bet
        if cap == 0 or mult_cap < cap:
            cap = mult_cap
    return cap


def _total_bet_minor(game: GameVersion) -> int:
    bet = game.bet_model
    if bet.total_bet_minor_units and bet.total_bet_minor_units > 0:
        return bet.total_bet_minor_units
    lines = bet.line_count or 1
    scale = bet.coin_value_scale or 1
    coin = bet.default_coin_value or 1
    return lines * coin * scale


def _theoretical_max_win_minor(game: GameVersion) -> int:
    total_bet = _total_bet_minor(game)
    max_paytable = 0
    for pay in game.paytable.pays:
        mult = _pay_multiplier(pay.multiplier)
        win = mult * total_bet
        max_paytable = max(max_paytable, win)
    jackpot_max = _max_jackpot_minor(game, total_bet)
    return max(max_paytable, jackpot_max)


def _pay_multiplier(value: int | float) -> int:
    if isinstance(value, float):
        return int(round(value))
    return int(value)


def _max_jackpot_minor(game: GameVersion, total_bet: int) -> int:
    maximum = 0
    for machine in game.state_machines.values():
        for state in machine.states.values():
            tiers = state.plugin_config.get("jackpotTiers")
            if not isinstance(tiers, dict):
                continue
            for value in tiers.values():
                win = _pay_multiplier(value) * total_bet
                maximum = max(maximum, win)
    return maximum
