"""Built-in plugin manifest and supported versions."""

from __future__ import annotations

from dataclasses import dataclass

SUPPORTED_PLUGIN_VERSIONS: dict[str, frozenset[str]] = {
    "core.base-game": frozenset({"1.0.0"}),
    "core.free-spins": frozenset({"1.0.0"}),
    "core.hold-and-win": frozenset({"1.0.0"}),
    "core.multiplier": frozenset({"1.0.0"}),
}


@dataclass(frozen=True, slots=True)
class PluginDescriptor:
    plugin_id: str
    version: str
    config_schema_version: str = "1.0.0"


BUILT_IN_PLUGINS: tuple[PluginDescriptor, ...] = (
    PluginDescriptor("core.base-game", "1.0.0"),
    PluginDescriptor("core.free-spins", "1.0.0"),
    PluginDescriptor("core.hold-and-win", "1.0.0"),
    PluginDescriptor("core.multiplier", "1.0.0"),
)


def is_supported_plugin_version(plugin_id: str, version: str) -> bool:
    versions = SUPPORTED_PLUGIN_VERSIONS.get(plugin_id)
    return versions is not None and version in versions
