"""PluginHost — resolve, instantiate, and lifecycle orchestration (§11)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from runtime_core.domain.plugins import PluginRef
from runtime_core.plugins.contracts import (
    FeaturePlugin,
    FeatureStepResult,
    PluginContext,
    PluginFactory,
)
from runtime_core.plugins.exceptions import PluginLifecycleError
from runtime_core.runtime.plugins.registry import (
    PluginRegistry,
    default_builtin_registry,
)
from runtime_core.runtime.plugins.validation import validate_plugin_ref
from runtime_core.runtime.rng.protocol import RNG
from runtime_core.runtime.stack.frame import StateMachineFrame


@dataclass
class PluginHandle:
    """Active plugin binding for one stack frame state."""

    plugin: FeaturePlugin
    context: PluginContext
    enter_result: FeatureStepResult | None = field(default=None, repr=False)
    _entered: bool = field(default=False, repr=False)
    _released: bool = field(default=False, repr=False)


class PluginHost:
    """Resolves plugins from the static registry and manages lifecycle hooks."""

    def __init__(self, registry: PluginRegistry | None = None) -> None:
        self._registry = registry or default_builtin_registry()

    @property
    def registry(self) -> PluginRegistry:
        return self._registry

    def resolve_factory(self, plugin_id: str, version: str) -> PluginFactory:
        validate_plugin_version(plugin_id, version)
        return self._registry.resolve(plugin_id, version)

    def validate_plugin_ref(self, plugin_ref: PluginRef) -> None:
        validate_plugin_ref(plugin_ref, self._registry)

    def bind(
        self,
        plugin_ref: PluginRef,
        frame: StateMachineFrame,
        *,
        plugin_config: dict[str, Any] | None = None,
        game_bindings: PluginGameBindings | None = None,
    ) -> PluginHandle:
        """Instantiate plugin and invoke ``on_enter``."""
        self.validate_plugin_ref(plugin_ref)
        factory = self._registry.resolve(
            plugin_ref.plugin_id,
            plugin_ref.plugin_version,
        )
        plugin = factory.create()
        context = _build_context(
            plugin_ref,
            frame,
            plugin_config or {},
            game_bindings,
        )
        handle = PluginHandle(plugin=plugin, context=context)
        plugin.on_enter(context)
        handle._entered = True
        enter_hook = getattr(plugin, "enter_result", None)
        if callable(enter_hook):
            handle.enter_result = enter_hook()
        return handle

    def apply_enter_result(self, handle: PluginHandle) -> FeatureStepResult | None:
        """Apply optional counter/frame patches produced during ``on_enter``."""
        _ensure_active(handle)
        result = handle.enter_result
        if result is None:
            return None
        from runtime_core.runtime.plugins.counters import apply_step_side_effects

        apply_step_side_effects(handle.context.frame_context, result)
        handle.enter_result = None
        return result

    def execute_step(self, handle: PluginHandle, rng: RNG) -> FeatureStepResult:
        """Invoke ``execute_step`` on an active handle."""
        _ensure_active(handle)
        return handle.plugin.execute_step(handle.context, rng)

    def release(self, handle: PluginHandle) -> None:
        """Invoke ``on_exit`` and mark handle released."""
        if handle._released:
            msg = "plugin handle already released"
            raise PluginLifecycleError(msg)
        if not handle._entered:
            msg = "cannot release plugin handle that was never entered"
            raise PluginLifecycleError(msg)
        handle.plugin.on_exit(handle.context)
        handle._released = True


def validate_plugin_version(plugin_id: str, version: str) -> None:
    from runtime_core.plugins.exceptions import PluginVersionError
    from runtime_core.plugins.manifest import is_supported_plugin_version

    if not is_supported_plugin_version(plugin_id, version):
        msg = f"plugin version {version!r} is not supported for {plugin_id!r}"
        raise PluginVersionError(msg)


def _build_context(
    plugin_ref: PluginRef,
    frame: StateMachineFrame,
    plugin_config: dict[str, Any],
    game_bindings: PluginGameBindings | None,
) -> PluginContext:
    return PluginContext(
        plugin_id=plugin_ref.plugin_id,
        plugin_version=plugin_ref.plugin_version,
        config_schema_version=plugin_ref.config_schema_version,
        plugin_config=plugin_config,
        frame_context=frame.frame_context,
        rtp_category=frame.rtp_category,
        frame_id=frame.frame_id,
        machine_id=frame.machine_id,
        state_id=frame.state_id,
        plugin_ref_id=plugin_ref.ref_id,
        game_bindings=game_bindings,
    )


def _ensure_active(handle: PluginHandle) -> None:
    if handle._released:
        msg = "plugin handle has been released"
        raise PluginLifecycleError(msg)
    if not handle._entered:
        msg = "plugin handle was never entered"
        raise PluginLifecycleError(msg)
