"""Canonical domain model (GameVersion and related types)."""

from runtime_core.domain.game_version import (
    BetModel,
    Determinism,
    Exposure,
    GameConfig,
    GameVersion,
    GameVersionMeta,
    GridSpec,
    Metadata,
    Precedence,
    SessionConfig,
)
from runtime_core.domain.plugins import (
    Paytable,
    PaytableEntry,
    PluginRef,
    ReelSet,
    ReelStrip,
    RtpCategoryDef,
    RtpCategoryRegistryDoc,
    RuntimeLimits,
    WinModel,
)
from runtime_core.domain.state_machine import (
    Progression,
    State,
    StateMachine,
    Transition,
)

__all__ = [
    "BetModel",
    "Determinism",
    "Exposure",
    "GameConfig",
    "GameVersion",
    "GameVersionMeta",
    "GridSpec",
    "Metadata",
    "Paytable",
    "PaytableEntry",
    "PluginRef",
    "Precedence",
    "Progression",
    "ReelSet",
    "ReelStrip",
    "RtpCategoryDef",
    "RtpCategoryRegistryDoc",
    "RuntimeLimits",
    "SessionConfig",
    "State",
    "StateMachine",
    "Transition",
    "WinModel",
]
