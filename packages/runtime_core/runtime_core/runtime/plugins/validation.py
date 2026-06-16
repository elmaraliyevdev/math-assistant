"""Runtime plugin reference validation."""

from __future__ import annotations

from runtime_core.domain.plugins import PluginRef
from runtime_core.plugins.exceptions import PluginNotFoundError, PluginVersionError
from runtime_core.plugins.manifest import is_supported_plugin_version
from runtime_core.runtime.plugins.registry import PluginRegistry


def validate_plugin_ref(plugin_ref: PluginRef, registry: PluginRegistry) -> None:
    """Verify *plugin_ref* exists in *registry* with a supported version."""
    if not is_supported_plugin_version(plugin_ref.plugin_id, plugin_ref.plugin_version):
        msg = (
            f"plugin version {plugin_ref.plugin_version!r} is not supported "
            f"for {plugin_ref.plugin_id!r}"
        )
        raise PluginVersionError(msg)
    if not registry.is_registered(plugin_ref.plugin_id, plugin_ref.plugin_version):
        msg = (
            f"plugin {plugin_ref.plugin_id!r} version "
            f"{plugin_ref.plugin_version!r} is not registered"
        )
        raise PluginNotFoundError(msg)
