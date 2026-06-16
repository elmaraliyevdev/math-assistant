"""Free Spins plugin configuration parsing."""

from __future__ import annotations

from dataclasses import dataclass

from runtime_core.plugins.exceptions import PluginConfigurationError


@dataclass(frozen=True, slots=True)
class RetriggerConfig:
    enabled: bool
    awards_by_scatter_count: dict[int, int]


@dataclass(frozen=True, slots=True)
class FreeSpinsConfig:
    reel_set_id: str
    awards_by_scatter_count: dict[int, int]
    retrigger: RetriggerConfig | None = None


def parse_free_spins_config(raw: dict[str, object]) -> FreeSpinsConfig:
    reel_set_id = str(raw["reelSetId"])
    awards = _parse_award_map(raw["awardsByScatterCount"])
    if not awards:
        msg = "awardsByScatterCount must contain at least one entry"
        raise PluginConfigurationError(msg)
    retrigger_raw = raw.get("retrigger")
    retrigger: RetriggerConfig | None = None
    if isinstance(retrigger_raw, dict):
        enabled = bool(retrigger_raw.get("enabled", False))
        retrigger_awards: dict[int, int] = {}
        if enabled:
            awards_raw = retrigger_raw.get("awardsByScatterCount")
            if not isinstance(awards_raw, dict):
                msg = "retrigger requires awardsByScatterCount when enabled"
                raise PluginConfigurationError(msg)
            retrigger_awards = _parse_award_map(awards_raw)
        retrigger = RetriggerConfig(
            enabled=enabled,
            awards_by_scatter_count=retrigger_awards,
        )
    return FreeSpinsConfig(
        reel_set_id=reel_set_id,
        awards_by_scatter_count=awards,
        retrigger=retrigger,
    )


def lookup_scatter_award(awards: dict[int, int], scatter_count: int) -> int:
    if scatter_count in awards:
        return awards[scatter_count]
    msg = f"no award configured for scatter count {scatter_count}"
    raise PluginConfigurationError(msg)


def _parse_award_map(raw: object) -> dict[int, int]:
    if not isinstance(raw, dict):
        msg = "award map must be an object"
        raise PluginConfigurationError(msg)
    awards: dict[int, int] = {}
    for key, value in raw.items():
        awards[int(str(key))] = int(value)  # type: ignore[arg-type]
    return awards
