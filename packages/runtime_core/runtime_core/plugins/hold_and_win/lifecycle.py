"""Hold & Win lifecycle helpers."""

from __future__ import annotations

from runtime_core.plugins.contracts import CounterUpdateRequest, FeatureStepResult, PluginContext
from runtime_core.plugins.exceptions import PluginConfigurationError
from runtime_core.plugins.hold_and_win.config import HoldAndWinConfig
from runtime_core.plugins.hold_and_win.grid import HeldSymbolDict, normalize_held_symbols
from runtime_core.plugins.hold_and_win.wins import evaluate_hold_and_win_wins, initial_jackpot_tracking

_HAW_INITIALIZED_KEY = "hawInitialized"
_HELD_SYMBOLS_KEY = "heldSymbols"
_JACKPOT_TRACKING_KEY = "jackpotTracking"
_HAW_STEP_COUNT_KEY = "hawStepCount"


def build_enter_result(
    ctx: PluginContext,
    config: HoldAndWinConfig,
) -> FeatureStepResult:
    held = resolve_entry_held_symbols(ctx, config)
    if len(held) < config.trigger_symbol_count:
        msg = (
            f"hold and win entry requires at least {config.trigger_symbol_count} "
            f"trigger symbols, got {len(held)}"
        )
        raise PluginConfigurationError(msg)
    held = held[: config.grid_capacity]
    held = _with_default_multipliers(held, config)
    return FeatureStepResult(
        counter_updates=[
            CounterUpdateRequest(field="respinsRemaining", after=config.initial_respins),
        ],
        frame_local_patch={
            _HAW_INITIALIZED_KEY: True,
            _HELD_SYMBOLS_KEY: held,
            _JACKPOT_TRACKING_KEY: initial_jackpot_tracking(config),
            _HAW_STEP_COUNT_KEY: 0,
        },
    )


def resolve_entry_held_symbols(
    ctx: PluginContext,
    config: HoldAndWinConfig,
) -> list[HeldSymbolDict]:
    state = ctx.frame_context.frame_local_state
    raw = state.get("entryHeldSymbols")
    if isinstance(raw, list) and raw:
        return normalize_held_symbols(raw)
    raw_held = state.get(_HELD_SYMBOLS_KEY)
    if isinstance(raw_held, list) and raw_held:
        return normalize_held_symbols(raw_held)
    msg = "hold and win entry requires entryHeldSymbols in frame local state"
    raise PluginConfigurationError(msg)


def finalize_step_result(
    *,
    config: HoldAndWinConfig,
    held_before: list[HeldSymbolDict],
    new_symbols: list[HeldSymbolDict],
    respins_before: int,
    step_count: int,
    max_steps: int | None,
    total_bet_minor_units: int,
    jackpot_tracking: dict[str, bool],
    rng_draw_ids: list[int],
) -> FeatureStepResult:
    held_after = held_before + new_symbols
    if len(held_after) > config.grid_capacity:
        held_after = held_after[: config.grid_capacity]

    if new_symbols:
        respins_after = config.initial_respins
    else:
        respins_after = max(respins_before - 1, 0)

    force_complete = False
    if max_steps is not None and step_count + 1 > max_steps:
        respins_after = 0
        force_complete = True

    grid_full = len(held_after) >= config.grid_capacity
    feature_complete = (
        force_complete
        or respins_after == 0
        or (config.fill_ends_feature and grid_full)
    )

    wins: list[dict[str, object]] = []
    updated_tracking = dict(jackpot_tracking)
    if feature_complete:
        wins, updated_tracking = evaluate_hold_and_win_wins(
            config,
            held_after,
            total_bet_minor_units=total_bet_minor_units,
            jackpot_tracking=updated_tracking,
        )

    tokens: list[str] = []
    if feature_complete:
        tokens.append("FEATURE_COMPLETE")

    return FeatureStepResult(
        trigger_tokens=tokens,
        wins=wins,
        grid_outcome={
            "reelSetId": config.reel_set_id,
            "heldSymbols": held_after,
            "newSymbols": new_symbols,
            "rngDrawIds": rng_draw_ids,
        },
        counter_updates=[
            CounterUpdateRequest(field="respinsRemaining", after=respins_after),
        ],
        frame_local_patch={
            _HELD_SYMBOLS_KEY: held_after,
            _JACKPOT_TRACKING_KEY: updated_tracking,
            _HAW_STEP_COUNT_KEY: step_count + 1,
        },
    )


def _with_default_multipliers(
    held: list[HeldSymbolDict],
    config: HoldAndWinConfig,
) -> list[HeldSymbolDict]:
    normalized: list[HeldSymbolDict] = []
    for symbol in held:
        symbol_id = str(symbol["symbolId"])
        multiplier = config.symbol_values.get(
            symbol_id,
            int(symbol.get("valueMultiplier", 1)),
        )
        normalized.append(
            {
                "reel": int(symbol["reel"]),
                "row": int(symbol["row"]),
                "symbolId": symbol_id,
                "valueMultiplier": multiplier,
            },
        )
    return normalized
