"""Plugin manifest tests."""

from __future__ import annotations

from runtime_core.plugins.manifest import (
    BUILT_IN_PLUGINS,
    is_supported_plugin_version,
)


def test_builtin_plugin_ids() -> None:
    ids = {descriptor.plugin_id for descriptor in BUILT_IN_PLUGINS}
    assert ids == {
        "core.base-game",
        "core.free-spins",
        "core.hold-and-win",
        "core.multiplier",
    }


def test_is_supported_plugin_version() -> None:
    assert is_supported_plugin_version("core.base-game", "1.0.0") is True
    assert is_supported_plugin_version("core.base-game", "2.0.0") is False
    assert is_supported_plugin_version("core.unknown", "1.0.0") is False
