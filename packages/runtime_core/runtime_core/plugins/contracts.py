"""Feature plugin contracts for Runtime Core §11–§12."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol

from runtime_core.plugins.bindings import PluginGameBindings
from runtime_core.runtime.rng.protocol import RNG

if TYPE_CHECKING:
    from runtime_core.runtime.frames import FrameContext


@dataclass
class FeatureStepResult:
    """Output of one plugin ``execute_step`` call (RUNTIME_CORE_DESIGN §6.3)."""

    trigger_tokens: list[str] = field(default_factory=list)
    consume_step: bool = True
    frame_local_patch: dict[str, Any] = field(default_factory=dict)
    wins: list[dict[str, Any]] = field(default_factory=list)
    grid_outcome: dict[str, Any] | None = None
    counter_updates: list[CounterUpdateRequest] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class CounterUpdateRequest:
    """Requested mutation of a frame counter field (Runtime Core applies)."""

    field: str
    after: int


@dataclass(frozen=True, slots=True)
class PluginContext:
    """Immutable binding context passed to plugin lifecycle hooks."""

    plugin_id: str
    plugin_version: str
    config_schema_version: str
    plugin_config: dict[str, Any]
    frame_context: FrameContext
    rtp_category: str
    frame_id: str
    machine_id: str
    state_id: str
    plugin_ref_id: str
    game_bindings: PluginGameBindings | None = None


class FeaturePlugin(Protocol):
    """Built-in feature plugin interface (§12.1)."""

    @property
    def plugin_id(self) -> str: ...

    @property
    def plugin_version(self) -> str: ...

    def on_enter(self, ctx: PluginContext) -> None: ...

    def execute_step(self, ctx: PluginContext, rng: RNG) -> FeatureStepResult: ...

    def on_exit(self, ctx: PluginContext) -> None: ...


class PluginFactory(Protocol):
    """Creates a fresh plugin instance for one state binding."""

    def create(self) -> FeaturePlugin: ...
