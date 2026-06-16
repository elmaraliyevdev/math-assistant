"""Plugin host test helpers."""

from __future__ import annotations

from dataclasses import dataclass, field

from runtime_core.domain.plugins import PluginRef
from runtime_core.plugins.contracts import (
    FeaturePlugin,
    FeatureStepResult,
    PluginContext,
)
from runtime_core.plugins.manifest import PluginDescriptor
from runtime_core.runtime.frames import new_frame_context
from runtime_core.runtime.rng.protocol import RNG
from runtime_core.runtime.stack import build_frame


@dataclass
class RecordingPlugin(FeaturePlugin):
    plugin_id: str = "core.base-game"
    plugin_version: str = "1.0.0"
    events: list[str] = field(default_factory=list)
    step_result: FeatureStepResult = field(default_factory=FeatureStepResult)

    def on_enter(self, ctx: PluginContext) -> None:
        self.events.append(f"enter:{ctx.state_id}")

    def execute_step(self, ctx: PluginContext, rng: RNG) -> FeatureStepResult:
        self.events.append(f"step:{ctx.state_id}:{rng.draw_id}")
        return self.step_result

    def on_exit(self, ctx: PluginContext) -> None:
        self.events.append(f"exit:{ctx.state_id}")


@dataclass(frozen=True, slots=True)
class RecordingFactory:
    plugin: RecordingPlugin

    def create(self) -> FeaturePlugin:
        return self.plugin


def base_plugin_ref() -> PluginRef:
    return PluginRef(
        ref_id="base_main",
        plugin_id="core.base-game",
        plugin_version="1.0.0",
        config_schema_version="1.0.0",
        capabilities=["spin.grid"],
    )


def base_frame():
    from runtime_core.domain.state_machine import State

    state = State(
        id="BASE",
        plugin_ref_id="base_main",
        state_type="atomic_spin",
        rtp_category="BASE",
    )
    return build_frame(
        frame_id="f-0-0",
        machine_id="main",
        state=state,
        frame_context=new_frame_context(),
    )


def descriptor_for(ref: PluginRef) -> PluginDescriptor:
    return PluginDescriptor(
        plugin_id=ref.plugin_id,
        version=ref.plugin_version,
        config_schema_version=ref.config_schema_version,
    )
