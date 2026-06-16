"""Plugin reference, version, capability, and config validation."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.plugins.manifest import is_supported_plugin_version
from runtime_core.validation.graph_validator import _add_findings
from runtime_core.validation.report import ValidationFinding, ValidationReport
from runtime_core.validation.schema_validator import SchemaValidator
from runtime_core.validation.validators.plugin_config_validator import (
    validate_plugin_references,
)
from runtime_core.validation.validators.rtp_registry import RtpCategoryRegistry

_REQUIRED_CAPABILITIES: dict[str, list[str]] = {
    "atomic_spin": ["spin.grid"],
    "multi_step": ["spin.grid", "state.multistep"],
}


class PluginValidator:
    def __init__(
        self,
        schema: SchemaValidator | None,
        rtp_registry: RtpCategoryRegistry | None,
    ) -> None:
        self._schema = schema
        self._rtp_registry = rtp_registry

    def validate(self, game: GameVersion | None) -> ValidationReport:
        report = ValidationReport.empty()
        if game is None:
            return report
        rtp = self._rtp_registry.clone() if self._rtp_registry is not None else None
        if rtp is not None:
            rtp.merge_document(game)
        for machine_id, machine in game.state_machines.items():
            for state_id, state in machine.states.items():
                state_path = f"stateMachines.{machine_id}.states.{state_id}"
                plugin = game.plugins.get(state.plugin_ref_id)
                if plugin is None:
                    from runtime_core.validation.issues import graph_plugin_ref_missing

                    report.add_error(
                        graph_plugin_ref_missing(state_path, state.plugin_ref_id)
                    )
                    continue
                if not is_supported_plugin_version(
                    plugin.plugin_id, plugin.plugin_version
                ):
                    from runtime_core.validation.issues import (
                        graph_plugin_version_unsupported,
                    )

                    report.add_error(
                        graph_plugin_version_unsupported(
                            plugin.ref_id,
                            plugin.plugin_id,
                            plugin.plugin_version,
                        ),
                    )
                for capability in _required_capabilities_for_state(state.state_type):
                    if capability not in plugin.capabilities:
                        from runtime_core.validation.issues import (
                            graph_plugin_capability_missing,
                        )

                        report.add_error(
                            graph_plugin_capability_missing(plugin.ref_id, capability),
                        )
                if (
                    rtp is not None
                    and state.rtp_category
                    and not rtp.is_known(state.rtp_category)
                ):
                    from runtime_core.validation.issues import (
                        graph_rtp_category_unknown,
                    )

                    report.add_error(
                        graph_rtp_category_unknown(
                            f"{state_path}.rtpCategory",
                            state.rtp_category,
                        ),
                    )
                if self._schema is not None:
                    config_path = f"{state_path}.pluginConfig"
                    for finding in self._schema.validate_plugin_config(
                        plugin.plugin_id,
                        plugin.config_schema_version,
                        state.plugin_config,
                    ):
                        if isinstance(finding, ValidationFinding):
                            report.add_error(
                                finding.model_copy(update={"path": config_path})
                            )
        _add_findings(report, validate_plugin_references(game))
        return report


def _required_capabilities_for_state(state_type: str) -> list[str]:
    return _REQUIRED_CAPABILITIES.get(state_type, [])
