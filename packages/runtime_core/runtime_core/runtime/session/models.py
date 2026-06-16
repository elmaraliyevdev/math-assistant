"""Session value types for Runtime Core R1."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BetContext:
    line_count: int
    coin_value_scale: int
    default_coin_value: int
    total_bet_minor_units: int
    bet_model_type: str


@dataclass(frozen=True, slots=True)
class EffectiveLimits:
    max_steps_per_spin_chain: int
    max_frames_per_chain: int
    max_transitions_per_step: int
    max_respins_per_feature: int
    max_events_per_chain: int
    max_wall_clock_ms_per_chain: int


@dataclass(frozen=True, slots=True)
class ExposureState:
    enforce_cap: bool
    effective_cap_minor: int
    cap_scope: str
    max_win_minor_units: int
    max_win_multiplier: int
