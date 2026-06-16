"""PluginHost lifecycle and resolution tests."""

from __future__ import annotations

import pytest

from runtime_core.plugins.contracts import FeatureStepResult
from runtime_core.plugins.exceptions import (
    PluginLifecycleError,
    PluginNotFoundError,
    PluginNotImplementedError,
    PluginVersionError,
)
from runtime_core.plugins.manifest import BUILT_IN_PLUGINS
from runtime_core.plugins.manifest import BUILT_IN_PLUGINS
from runtime_core.runtime.plugins.host import PluginHandle, PluginHost, validate_plugin_version
from runtime_core.runtime.plugins.registry import PluginRegistry, default_builtin_registry
from runtime_core.runtime.rng import RNGService
from tests.runtime.plugins.conftest import (
    RecordingFactory,
    RecordingPlugin,
    base_frame,
    base_plugin_ref,
    descriptor_for,
)


def _host_with_recording_plugin() -> tuple[PluginHost, RecordingPlugin]:
    plugin = RecordingPlugin()
    registry = PluginRegistry()
    ref = base_plugin_ref()
    registry.register(descriptor_for(ref), RecordingFactory(plugin=plugin))
    return PluginHost(registry), plugin


def test_resolve_factory_known_plugin() -> None:
    host = PluginHost(default_builtin_registry())
    factory = host.resolve_factory("core.hold-and-win", "1.0.0")
    assert factory is not None


def test_resolve_factory_unknown_plugin() -> None:
    host = PluginHost(default_builtin_registry())
    with pytest.raises(PluginVersionError):
        host.resolve_factory("core.unknown", "1.0.0")


def test_resolve_factory_version_mismatch() -> None:
    host = PluginHost(default_builtin_registry())
    with pytest.raises(PluginVersionError):
        host.resolve_factory("core.base-game", "2.0.0")


def test_validate_plugin_version_helper() -> None:
    with pytest.raises(PluginVersionError):
        validate_plugin_version("core.base-game", "0.0.1")


def test_bind_instantiates_and_calls_on_enter() -> None:
    host, plugin = _host_with_recording_plugin()
    handle = host.bind(base_plugin_ref(), base_frame(), plugin_config={"reelSetId": "base"})
    assert handle.context.plugin_config == {"reelSetId": "base"}
    assert plugin.events == ["enter:BASE"]


def test_execute_step_calls_plugin() -> None:
    host, plugin = _host_with_recording_plugin()
    plugin.step_result = FeatureStepResult(trigger_tokens=["SPIN_COMPLETE"])
    handle = host.bind(base_plugin_ref(), base_frame())
    rng = RNGService(None).new_chain_scope(b"s", 0, "run", 0).frame_stream("f-0-0").step_rng(0)
    result = host.execute_step(handle, rng)
    assert result.trigger_tokens == ["SPIN_COMPLETE"]
    assert plugin.events[1].startswith("step:BASE:")


def test_release_calls_on_exit() -> None:
    host, plugin = _host_with_recording_plugin()
    handle = host.bind(base_plugin_ref(), base_frame())
    host.release(handle)
    assert plugin.events == ["enter:BASE", "exit:BASE"]


def test_lifecycle_ordering_enter_step_exit() -> None:
    host, plugin = _host_with_recording_plugin()
    handle = host.bind(base_plugin_ref(), base_frame())
    rng = RNGService(None).new_chain_scope(b"s", 0, "run", 0).frame_stream("f-0-0").step_rng(0)
    host.execute_step(handle, rng)
    host.release(handle)
    assert plugin.events[0].startswith("enter:")
    assert plugin.events[1].startswith("step:")
    assert plugin.events[2].startswith("exit:")


def test_double_release_raises() -> None:
    host, _plugin = _host_with_recording_plugin()
    handle = host.bind(base_plugin_ref(), base_frame())
    host.release(handle)
    with pytest.raises(PluginLifecycleError, match="already released"):
        host.release(handle)


def test_execute_step_after_release_raises() -> None:
    host, _plugin = _host_with_recording_plugin()
    handle = host.bind(base_plugin_ref(), base_frame())
    host.release(handle)
    rng = RNGService(None).new_chain_scope(b"s", 0, "run", 0).frame_stream("f-0-0").step_rng(0)
    with pytest.raises(PluginLifecycleError, match="released"):
        host.execute_step(handle, rng)


def test_bind_unimplemented_factory_raises_on_create() -> None:
    from runtime_core.domain.plugins import PluginRef
    from runtime_core.runtime.plugins.registry import PluginRegistry, _NotImplementedFactory

    registry = PluginRegistry()
    registry.register(
        BUILT_IN_PLUGINS[3],
        _NotImplementedFactory(BUILT_IN_PLUGINS[3]),
    )
    host = PluginHost(registry)
    ref = PluginRef(
        ref_id="stub",
        plugin_id="core.multiplier",
        plugin_version="1.0.0",
        config_schema_version="1.0.0",
        capabilities=["multiplier.apply"],
    )
    with pytest.raises(PluginNotImplementedError):
        host.bind(ref, base_frame())


def test_validate_plugin_ref_on_host() -> None:
    host, _plugin = _host_with_recording_plugin()
    host.validate_plugin_ref(base_plugin_ref())


def test_validate_plugin_ref_rejects_bad_version() -> None:
    host = PluginHost(default_builtin_registry())
    ref = base_plugin_ref().model_copy(update={"plugin_version": "9.9.9"})
    with pytest.raises(PluginVersionError):
        host.validate_plugin_ref(ref)


def test_resolve_unregistered_supported_version() -> None:
    host = PluginHost(PluginRegistry())
    with pytest.raises(PluginNotFoundError):
        host.resolve_factory("core.base-game", "1.0.0")


def test_release_without_enter_raises() -> None:
    host, _plugin = _host_with_recording_plugin()
    handle = host.bind(base_plugin_ref(), base_frame())
    handle._entered = False
    with pytest.raises(PluginLifecycleError, match="never entered"):
        host.release(handle)


def test_execute_step_without_enter_raises() -> None:
    host, plugin = _host_with_recording_plugin()
    bound = host.bind(base_plugin_ref(), base_frame())
    handle = PluginHandle(plugin=plugin, context=bound.context, _entered=False)
    rng = RNGService(None).new_chain_scope(b"s", 0, "run", 0).frame_stream("f-0-0").step_rng(0)
    with pytest.raises(PluginLifecycleError, match="never entered"):
        host.execute_step(handle, rng)


def test_host_exposes_registry() -> None:
    registry = PluginRegistry()
    host = PluginHost(registry)
    assert host.registry is registry


def test_all_builtin_plugins_resolve_in_default_host() -> None:
    host = PluginHost(default_builtin_registry())
    for descriptor in BUILT_IN_PLUGINS:
        host.resolve_factory(descriptor.plugin_id, descriptor.version)
