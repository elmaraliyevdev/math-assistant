"""Plugin reference validation tests."""

from __future__ import annotations

import pytest
from tests.runtime.plugins.conftest import (
    RecordingFactory,
    RecordingPlugin,
    descriptor_for,
)

from runtime_core.domain.plugins import PluginRef
from runtime_core.plugins.exceptions import PluginNotFoundError, PluginVersionError
from runtime_core.runtime.plugins.registry import PluginRegistry
from runtime_core.runtime.plugins.validation import validate_plugin_ref


def test_validate_supported_registered_plugin() -> None:
    registry = PluginRegistry()
    ref = PluginRef(
        ref_id="base_main",
        plugin_id="core.base-game",
        plugin_version="1.0.0",
        config_schema_version="1.0.0",
        capabilities=["spin.grid"],
    )
    registry.register(
        descriptor_for(ref),
        RecordingFactory(plugin=RecordingPlugin()),
    )
    validate_plugin_ref(ref, registry)


def test_validate_unknown_plugin_id() -> None:
    registry = PluginRegistry()
    ref = PluginRef(
        ref_id="x",
        plugin_id="core.unknown",
        plugin_version="1.0.0",
        config_schema_version="1.0.0",
        capabilities=[],
    )
    with pytest.raises(PluginVersionError):
        validate_plugin_ref(ref, registry)


def test_validate_unsupported_version() -> None:
    registry = PluginRegistry()
    ref = PluginRef(
        ref_id="base_main",
        plugin_id="core.base-game",
        plugin_version="2.0.0",
        config_schema_version="1.0.0",
        capabilities=["spin.grid"],
    )
    with pytest.raises(PluginVersionError, match="not supported"):
        validate_plugin_ref(ref, registry)


def test_validate_supported_but_unregistered_version() -> None:
    registry = PluginRegistry()
    ref = PluginRef(
        ref_id="base_main",
        plugin_id="core.base-game",
        plugin_version="1.0.0",
        config_schema_version="1.0.0",
        capabilities=["spin.grid"],
    )
    with pytest.raises(PluginNotFoundError, match="not registered"):
        validate_plugin_ref(ref, registry)
