"""Validation Engine orchestrator."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass

from runtime_core.domain.game_version import GameVersion
from runtime_core.validation.exposure_validator import ExposureValidator
from runtime_core.validation.graph_validator import GraphValidator
from runtime_core.validation.limits_validator import LimitsValidator
from runtime_core.validation.plugin_validator import PluginValidator
from runtime_core.validation.report import ValidationReport
from runtime_core.validation.schema_paths import SchemaPaths, default_schema_paths
from runtime_core.validation.schema_validator import SchemaValidator
from runtime_core.validation.validators.priority_tiers import PriorityTierRegistry
from runtime_core.validation.validators.rtp_registry import RtpCategoryRegistry


class ValidationCancelledError(Exception):
    """Raised when validation is cancelled before completion."""


@dataclass(frozen=True, slots=True)
class ValidationEngineConfig:
    schema_paths: SchemaPaths | None = None


class ValidationEngine:
    """Runs schema → graph → plugin → exposure → limits validation."""

    def __init__(
        self,
        *,
        schema: SchemaValidator,
        graph: GraphValidator,
        plugin: PluginValidator,
        exposure: ExposureValidator,
        limits: LimitsValidator,
    ) -> None:
        self._schema = schema
        self._graph = graph
        self._plugin = plugin
        self._exposure = exposure
        self._limits = limits

    @classmethod
    def create(cls, config: ValidationEngineConfig | None = None) -> ValidationEngine:
        cfg = config or ValidationEngineConfig()
        paths = cfg.schema_paths or default_schema_paths()
        schema_root = paths.game_schema.parent.parent
        schema = SchemaValidator(
            game_schema=paths.game_schema,
            plugin_schema_dir=paths.plugin_schema_dir,
        )
        tiers = PriorityTierRegistry.load(schema_root)
        rtp = RtpCategoryRegistry.load(schema_root)
        return cls(
            schema=schema,
            graph=GraphValidator(tiers),
            plugin=PluginValidator(schema, rtp),
            exposure=ExposureValidator(),
            limits=LimitsValidator(),
        )

    def validate(
        self,
        game: GameVersion | None,
        *,
        should_cancel: Callable[[], bool] | None = None,
    ) -> ValidationReport:
        if should_cancel is not None and should_cancel():
            msg = "validation cancelled"
            raise ValidationCancelledError(msg)
        if game is None:
            msg = "game is nil"
            raise ValueError(msg)
        raw = json.dumps(game.to_json_dict(), separators=(",", ":")).encode("utf-8")
        schema_report = self._schema.validate_game_bytes(raw)
        if schema_report.has_errors():
            return schema_report
        report = ValidationReport.empty(
            content_hash=schema_report.metadata.game_content_hash or "",
        )
        if should_cancel is not None and should_cancel():
            msg = "validation cancelled"
            raise ValidationCancelledError(msg)
        report.merge(self._graph.validate(game))
        report.merge(self._plugin.validate(game))
        report.merge(self._exposure.validate(game))
        report.merge(self._limits.validate(game))
        return report
