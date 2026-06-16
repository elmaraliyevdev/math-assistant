"""Session bet, limits, exposure, and determinism resolution."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace

from runtime_core.domain.game_version import GameVersion
from runtime_core.runtime.session.models import (
    BetContext,
    EffectiveLimits,
    ExposureState,
)


def validate_determinism(game: GameVersion) -> None:
    determinism = game.determinism
    if determinism.rng_algorithm != "PCG64":
        msg = (
            f"unsupported determinism.rngAlgorithm {determinism.rng_algorithm!r} "
            "(MVP requires PCG64)"
        )
        raise ValueError(msg)
    policy = determinism.seed_derivation_policy
    if policy is not None and policy != "v1-hash-shard":
        msg = f"unsupported determinism.seedDerivationPolicy {policy!r}"
        raise ValueError(msg)
    money = determinism.money_representation
    if money is not None and money != "fixed_minor_units":
        msg = f"unsupported determinism.moneyRepresentation {money!r}"
        raise ValueError(msg)


def content_hash(game: GameVersion) -> str:
    if game.content_hash:
        return game.content_hash
    raw = json.dumps(
        game.to_json_dict(exclude_none=True),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def resolve_bet(game: GameVersion, override: int) -> tuple[BetContext, int]:
    bet = game.bet_model
    if override > 0:
        ctx = BetContext(
            line_count=bet.line_count or 0,
            coin_value_scale=bet.coin_value_scale,
            default_coin_value=bet.default_coin_value,
            total_bet_minor_units=override,
            bet_model_type=bet.type,
        )
        return ctx, override
    if bet.total_bet_minor_units is not None and bet.total_bet_minor_units > 0:
        total = bet.total_bet_minor_units
        ctx = BetContext(
            line_count=bet.line_count or 0,
            coin_value_scale=bet.coin_value_scale,
            default_coin_value=bet.default_coin_value,
            total_bet_minor_units=total,
            bet_model_type=bet.type,
        )
        return ctx, total
    lines = bet.line_count or 0
    if lines <= 0:
        lines = 1
    scale = bet.coin_value_scale
    if scale <= 0:
        scale = 1
    coin = bet.default_coin_value
    if coin <= 0:
        coin = 1
    total = lines * coin * scale
    ctx = BetContext(
        line_count=bet.line_count or 0,
        coin_value_scale=bet.coin_value_scale,
        default_coin_value=bet.default_coin_value,
        total_bet_minor_units=total,
        bet_model_type=bet.type,
    )
    return ctx, total


def platform_limits() -> EffectiveLimits:
    return EffectiveLimits(
        max_steps_per_spin_chain=500,
        max_frames_per_chain=8,
        max_transitions_per_step=8,
        max_respins_per_feature=100,
        max_events_per_chain=10000,
        max_wall_clock_ms_per_chain=0,
    )


def resolve_limits(game: GameVersion) -> EffectiveLimits:
    limits = platform_limits()
    runtime_limits = game.session.runtime_limits
    if runtime_limits is not None:
        updates: dict[str, int] = {}
        for field in (
            "max_steps_per_spin_chain",
            "max_frames_per_chain",
            "max_transitions_per_step",
            "max_respins_per_feature",
            "max_events_per_chain",
            "max_wall_clock_ms_per_chain",
        ):
            value = getattr(runtime_limits, field)
            if value is not None and value > 0:
                updates[field] = value
        if updates:
            limits = replace(limits, **updates)
    max_stack = game.session.max_stack_depth
    if max_stack <= 0:
        max_stack = 8
    max_frames = limits.max_frames_per_chain
    if max_frames <= 0 or max_frames > max_stack:
        limits = replace(limits, max_frames_per_chain=max_stack)
    return limits


def resolve_exposure(game: GameVersion, total_bet: int) -> ExposureState:
    exp = game.exposure
    multiplier = exp.max_win_multiplier or 0
    cap = exp.max_win_minor_units
    if multiplier > 0 and total_bet > 0:
        mult_cap = multiplier * total_bet
        if cap == 0 or mult_cap < cap:
            cap = mult_cap
    return ExposureState(
        enforce_cap=exp.enforce_cap,
        effective_cap_minor=cap,
        cap_scope=exp.cap_scope,
        max_win_minor_units=exp.max_win_minor_units,
        max_win_multiplier=multiplier,
    )


def resolve_inheritance_policy(game: GameVersion) -> str:
    policy = game.session.context_inheritance_policy
    return policy if policy else "mvp-v1"


def resolved_session_fields(
    game: GameVersion,
    bet_minor_units: int,
) -> tuple[str, BetContext, int, str, EffectiveLimits, ExposureState]:
    validate_determinism(game)
    game_hash = content_hash(game)
    bet, total_bet = resolve_bet(game, bet_minor_units)
    limits = resolve_limits(game)
    exposure = resolve_exposure(game, total_bet)
    policy = resolve_inheritance_policy(game)
    return game_hash, bet, total_bet, policy, limits, exposure
