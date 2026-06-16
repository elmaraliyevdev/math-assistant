"""Built-in plugin contracts and manifest."""

from runtime_core.plugins.contracts import (
    FeaturePlugin,
    FeatureStepResult,
    PluginContext,
    PluginFactory,
)
from runtime_core.plugins.exceptions import (
    PluginError,
    PluginLifecycleError,
    PluginNotFoundError,
    PluginNotImplementedError,
    PluginVersionError,
)
from runtime_core.plugins.manifest import (
    BUILT_IN_PLUGINS,
    SUPPORTED_PLUGIN_VERSIONS,
    PluginDescriptor,
    is_supported_plugin_version,
)

__all__ = [
    "BUILT_IN_PLUGINS",
    "SUPPORTED_PLUGIN_VERSIONS",
    "FeaturePlugin",
    "FeatureStepResult",
    "PluginContext",
    "PluginDescriptor",
    "PluginError",
    "PluginFactory",
    "PluginLifecycleError",
    "PluginNotFoundError",
    "PluginNotImplementedError",
    "PluginVersionError",
    "is_supported_plugin_version",
]
