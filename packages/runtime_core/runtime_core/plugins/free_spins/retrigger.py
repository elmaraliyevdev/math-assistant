"""Free Spins retrigger evaluation and runtime limit guards."""

from __future__ import annotations

from dataclasses import dataclass

from runtime_core.plugins.bindings import PluginGameBindings
from runtime_core.plugins.free_spins.config import FreeSpinsConfig, lookup_scatter_award


@dataclass(frozen=True, slots=True)
class RetriggerOutcome:
    award: int
    emit_token: bool
    retrigger_count: int


def evaluate_retrigger(
    config: FreeSpinsConfig,
    bindings: PluginGameBindings,
    *,
    scatter_count: int,
    current_retrigger_count: int,
) -> RetriggerOutcome:
    if config.retrigger is None or not config.retrigger.enabled:
        return RetriggerOutcome(award=0, emit_token=False, retrigger_count=current_retrigger_count)
    if scatter_count not in config.retrigger.awards_by_scatter_count:
        return RetriggerOutcome(award=0, emit_token=False, retrigger_count=current_retrigger_count)
    max_retriggers = bindings.max_retriggers_per_feature
    if max_retriggers is not None and current_retrigger_count >= max_retriggers:
        return RetriggerOutcome(award=0, emit_token=False, retrigger_count=current_retrigger_count)
    award = lookup_scatter_award(config.retrigger.awards_by_scatter_count, scatter_count)
    return RetriggerOutcome(
        award=award,
        emit_token=True,
        retrigger_count=current_retrigger_count + 1,
    )
