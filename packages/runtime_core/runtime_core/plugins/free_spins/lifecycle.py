"""Free Spins lifecycle helpers (initialization and step accounting)."""

from __future__ import annotations

from runtime_core.plugins.contracts import CounterUpdateRequest, FeatureStepResult, PluginContext
from runtime_core.plugins.exceptions import PluginConfigurationError
from runtime_core.plugins.free_spins.config import FreeSpinsConfig, lookup_scatter_award
from runtime_core.plugins.free_spins.retrigger import RetriggerOutcome, evaluate_retrigger

_FS_INITIALIZED_KEY = "fsInitialized"
_FS_RETRIGGER_COUNT_KEY = "fsRetriggerCount"
_FS_STEP_COUNT_KEY = "fsStepCount"


def build_enter_result(
    ctx: PluginContext,
    config: FreeSpinsConfig,
) -> FeatureStepResult:
    scatter_count = resolve_entry_scatter_count(ctx)
    initial_spins = lookup_scatter_award(config.awards_by_scatter_count, scatter_count)
    return FeatureStepResult(
        counter_updates=[
            CounterUpdateRequest(field="spinsRemaining", after=initial_spins),
        ],
        frame_local_patch={
            _FS_INITIALIZED_KEY: True,
            "entryScatterCount": scatter_count,
            _FS_RETRIGGER_COUNT_KEY: 0,
            _FS_STEP_COUNT_KEY: 0,
        },
    )


def resolve_entry_scatter_count(ctx: PluginContext) -> int:
    state = ctx.frame_context.frame_local_state
    scatter_counts = state.get("scatterCounts")
    if isinstance(scatter_counts, dict):
        scatter = scatter_counts.get("SCATTER")
        if scatter is not None:
            return int(scatter)
    entry = state.get("entryScatterCount")
    if entry is not None:
        return int(entry)
    msg = "free spins entry requires scatterCounts or entryScatterCount in frame local state"
    raise PluginConfigurationError(msg)


def finalize_step_result(
    spin_result: FeatureStepResult,
    *,
    spins_before: int,
    retrigger: RetriggerOutcome,
    max_steps: int | None,
    current_step_count: int,
) -> FeatureStepResult:
    if max_steps is not None and current_step_count + 1 > max_steps:
        spins_after = 0
        force_complete = True
    else:
        spins_after = spins_before + retrigger.award - 1
        if spins_after < 0:
            spins_after = 0
        force_complete = False

    counter_updates = list(spin_result.counter_updates)
    counter_updates.append(
        CounterUpdateRequest(field="spinsRemaining", after=spins_after),
    )

    frame_patch = dict(spin_result.frame_local_patch)
    frame_patch[_FS_RETRIGGER_COUNT_KEY] = retrigger.retrigger_count
    frame_patch[_FS_STEP_COUNT_KEY] = current_step_count + 1

    tokens = list(spin_result.trigger_tokens)
    if retrigger.emit_token and retrigger.award > 0:
        tokens.insert(0, "RETRIGGER")
    if spins_after == 0 or force_complete:
        if "FEATURE_COMPLETE" not in tokens:
            tokens.append("FEATURE_COMPLETE")

    return FeatureStepResult(
        trigger_tokens=tokens,
        consume_step=spin_result.consume_step,
        frame_local_patch=frame_patch,
        wins=spin_result.wins,
        grid_outcome=spin_result.grid_outcome,
        counter_updates=counter_updates,
    )
