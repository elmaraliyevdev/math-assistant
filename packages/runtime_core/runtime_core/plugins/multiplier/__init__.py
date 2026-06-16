"""core.multiplier built-in plugin."""

from runtime_core.plugins.multiplier.apply import (
    MultiplierApplyResult,
    apply_multiplier,
    resolve_multiplier_factor,
)
from runtime_core.plugins.multiplier.config import MultiplierConfig, parse_multiplier_config
from runtime_core.plugins.multiplier.plugin import MultiplierFactory, MultiplierPlugin

__all__ = [
    "MultiplierApplyResult",
    "MultiplierConfig",
    "MultiplierFactory",
    "MultiplierPlugin",
    "apply_multiplier",
    "parse_multiplier_config",
    "resolve_multiplier_factor",
]
