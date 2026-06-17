"""Canonical game design intent detection for calibration recommendations."""

from __future__ import annotations

from dataclasses import dataclass

from runtime_core.domain.game_version import GameVersion


@dataclass(frozen=True, slots=True)
class DesignIntent:
    """Features and constraints declared in the canonical game JSON."""

    has_free_spins: bool
    has_hold_and_win: bool
    has_jackpot: bool
    volatility_target: str | None
    max_win_minor_units: int
    max_win_multiplier: int | None
    enforce_exposure_cap: bool


def detect_design_intent(game: GameVersion) -> DesignIntent:
    """Infer which mechanics exist in the canonical design."""
    has_free_spins = False
    has_hold_and_win = False
    has_jackpot = False

    if "hold_and_win" in game.state_machines:
        has_hold_and_win = True

    for machine in game.state_machines.values():
        for state in machine.states.values():
            if state.rtp_category == "FREE_SPINS" or state.id == "FREE_SPINS":
                has_free_spins = True
            if state.rtp_category == "HOLD_AND_WIN" or state.id in {
                "HOLD_AND_WIN",
                "HAW_RESPINS",
            }:
                has_hold_and_win = True

            config = state.plugin_config
            bonus_triggers = config.get("bonusTriggers")
            if isinstance(bonus_triggers, list):
                for trigger in bonus_triggers:
                    if isinstance(trigger, dict) and trigger.get("emitTrigger") == "HOLD_AND_WIN":
                        has_hold_and_win = True

            jackpot_tiers = config.get("jackpotTiers")
            if isinstance(jackpot_tiers, dict) and jackpot_tiers:
                has_jackpot = True

    return DesignIntent(
        has_free_spins=has_free_spins,
        has_hold_and_win=has_hold_and_win,
        has_jackpot=has_jackpot,
        volatility_target=game.metadata.volatility_target,
        max_win_minor_units=game.exposure.max_win_minor_units,
        max_win_multiplier=game.exposure.max_win_multiplier,
        enforce_exposure_cap=game.exposure.enforce_cap,
    )


def component_allowed(intent: DesignIntent, component: str) -> bool:
    """Return True when tuning recommendations for a component are allowed."""
    if component == "BASE":
        return True
    if component == "FREE_SPINS":
        return intent.has_free_spins
    if component == "HOLD_AND_WIN":
        return intent.has_hold_and_win
    if component == "JACKPOT":
        return intent.has_jackpot
    return True
