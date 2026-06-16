"""core.free-spins built-in plugin."""

from runtime_core.plugins.free_spins.config import FreeSpinsConfig, parse_free_spins_config
from runtime_core.plugins.free_spins.lifecycle import build_enter_result, finalize_step_result
from runtime_core.plugins.free_spins.plugin import FreeSpinsFactory, FreeSpinsPlugin
from runtime_core.plugins.free_spins.retrigger import RetriggerOutcome, evaluate_retrigger

__all__ = [
    "FreeSpinsConfig",
    "FreeSpinsFactory",
    "FreeSpinsPlugin",
    "RetriggerOutcome",
    "build_enter_result",
    "evaluate_retrigger",
    "finalize_step_result",
    "parse_free_spins_config",
]
