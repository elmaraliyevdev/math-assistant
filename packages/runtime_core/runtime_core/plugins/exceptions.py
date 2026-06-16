"""Plugin host exceptions."""


class PluginError(Exception):
    """Base plugin host error."""


class PluginNotFoundError(PluginError):
    """No registered factory for the requested plugin id/version."""


class PluginVersionError(PluginError):
    """Plugin version is not supported by the runtime manifest."""


class PluginNotImplementedError(PluginError):
    """Plugin is registered but has no runtime implementation yet."""


class PluginLifecycleError(PluginError):
    """Invalid plugin lifecycle transition."""


class PluginConfigurationError(PluginError):
    """Plugin configuration or binding context is invalid."""
