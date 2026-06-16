"""Static plugin registry tests."""

from __future__ import annotations

import pytest

from runtime_core.plugins.exceptions import (
    PluginNotFoundError,
    PluginNotImplementedError,
)
from runtime_core.plugins.manifest import BUILT_IN_PLUGINS
from runtime_core.runtime.plugins.registry import (
    PluginRegistry,
    _NotImplementedFactory,
    default_builtin_registry,
)


def test_builtin_registry_registers_all_mvp_plugins() -> None:
    registry = default_builtin_registry()
    descriptors = registry.descriptors()
    assert len(descriptors) == len(BUILT_IN_PLUGINS)
    for descriptor in BUILT_IN_PLUGINS:
        assert registry.is_registered(descriptor.plugin_id, descriptor.version)


def test_resolve_known_plugin_factory() -> None:
    registry = default_builtin_registry()
    factory = registry.resolve("core.base-game", "1.0.0")
    assert factory is not None


def test_resolve_unknown_plugin_raises() -> None:
    registry = default_builtin_registry()
    with pytest.raises(PluginNotFoundError, match="not registered"):
        registry.resolve("core.unknown", "1.0.0")


def test_resolve_unknown_version_raises() -> None:
    registry = default_builtin_registry()
    with pytest.raises(PluginNotFoundError, match="not registered"):
        registry.resolve("core.base-game", "9.9.9")


def test_default_factory_raises_not_implemented() -> None:
    registry = PluginRegistry()
    registry.register(BUILT_IN_PLUGINS[3], _NotImplementedFactory(BUILT_IN_PLUGINS[3]))
    with pytest.raises(PluginNotImplementedError, match="not implemented"):
        registry.resolve("core.multiplier", "1.0.0").create()


def test_implemented_hold_and_win_factory_creates_plugin() -> None:
    registry = default_builtin_registry()
    plugin = registry.resolve("core.hold-and-win", "1.0.0").create()
    assert plugin.plugin_id == "core.hold-and-win"


def test_implemented_free_spins_factory_creates_plugin() -> None:
    registry = default_builtin_registry()
    plugin = registry.resolve("core.free-spins", "1.0.0").create()
    assert plugin.plugin_id == "core.free-spins"


def test_implemented_base_game_factory_creates_plugin() -> None:
    registry = default_builtin_registry()
    plugin = registry.resolve("core.base-game", "1.0.0").create()
    assert plugin.plugin_id == "core.base-game"


def test_implemented_multiplier_factory_creates_plugin() -> None:
    registry = default_builtin_registry()
    plugin = registry.resolve("core.multiplier", "1.0.0").create()
    assert plugin.plugin_id == "core.multiplier"


def test_custom_factory_registration() -> None:
    from tests.runtime.plugins.conftest import RecordingFactory, RecordingPlugin

    registry = PluginRegistry()
    plugin = RecordingPlugin(plugin_id="core.multiplier")
    registry.register(
        BUILT_IN_PLUGINS[3],
        RecordingFactory(plugin=plugin),
    )
    created = registry.resolve("core.multiplier", "1.0.0").create()
    assert created.plugin_id == "core.multiplier"
