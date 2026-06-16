"""Priority tier registry loader."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PriorityTier:
    id: str
    default_priority: int
    range_min: int
    range_max: int
    aliases: tuple[str, ...]


class PriorityTierRegistry:
    def __init__(self, by_id: dict[str, PriorityTier]) -> None:
        self._by_id = by_id

    @classmethod
    def load(cls, schema_root: Path) -> PriorityTierRegistry:
        path = schema_root / "registries" / "priority-tiers-v1.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        by_id: dict[str, PriorityTier] = {}
        for tier_doc in doc["tiers"]:
            tier = PriorityTier(
                id=tier_doc["id"],
                default_priority=tier_doc["defaultPriority"],
                range_min=tier_doc["numericRange"]["min"],
                range_max=tier_doc["numericRange"]["max"],
                aliases=tuple(tier_doc.get("aliases", [])),
            )
            by_id[tier.id] = tier
            for alias in tier.aliases:
                by_id[alias] = tier
        return cls(by_id)

    def resolve(self, tier_id: str) -> PriorityTier | None:
        return self._by_id.get(tier_id)
