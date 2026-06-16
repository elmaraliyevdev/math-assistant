"""Static plugin registry."""

from __future__ import annotations

from dataclasses import dataclass

from runtime_core.plugins.base_game import BaseGameFactory
from runtime_core.plugins.contracts import FeaturePlugin, PluginFactory
from runtime_core.plugins.exceptions import (
    PluginNotFoundError,
    PluginNotImplementedError,
)
from runtime_core.plugins.free_spins import FreeSpinsFactory
from runtime_core.plugins.hold_and_win import HoldAndWinFactory
from runtime_core.plugins.manifest import BUILT_IN_PLUGINS, PluginDescriptor
from runtime_core.plugins.multiplier import MultiplierFactory


@dataclass(frozen=True, slots=True)
class _NotImplementedFactory:
    descriptor: PluginDescriptor

    def create(self) -> FeaturePlugin:
        msg = (
            f"plugin {self.descriptor.plugin_id}@{self.descriptor.version} "
            "is registered but not implemented"
        )
        raise PluginNotImplementedError(msg)


class PluginRegistry:
    """Compile-time static registry mapping ``(plugin_id, version)`` to factories."""

    def __init__(self) -> None:
        self._factories: dict[tuple[str, str], PluginFactory] = {}

    def register(self, descriptor: PluginDescriptor, factory: PluginFactory) -> None:
        key = (descriptor.plugin_id, descriptor.version)
        self._factories[key] = factory

    def resolve(self, plugin_id: str, version: str) -> PluginFactory:
        factory = self._factories.get((plugin_id, version))
        if factory is None:
            msg = f"plugin {plugin_id!r} version {version!r} is not registered"
            raise PluginNotFoundError(msg)
        return factory

    def is_registered(self, plugin_id: str, version: str) -> bool:
        return (plugin_id, version) in self._factories

    def descriptors(self) -> tuple[PluginDescriptor, ...]:
        keys = set(self._factories)
        return tuple(
            descriptor
            for descriptor in BUILT_IN_PLUGINS
            if (descriptor.plugin_id, descriptor.version) in keys
        )


def default_builtin_registry() -> PluginRegistry:
    """Registry with MVP built-in descriptors; M5a plugins are implemented."""
    registry = PluginRegistry()
    implemented: dict[str, PluginFactory] = {
        "core.base-game": BaseGameFactory(),
        "core.free-spins": FreeSpinsFactory(),
        "core.hold-and-win": HoldAndWinFactory(),
        "core.multiplier": MultiplierFactory(),
    }
    for descriptor in BUILT_IN_PLUGINS:
        factory = implemented.get(descriptor.plugin_id)
        if factory is None:
            factory = _NotImplementedFactory(descriptor)
        registry.register(descriptor, factory)
    return registry
