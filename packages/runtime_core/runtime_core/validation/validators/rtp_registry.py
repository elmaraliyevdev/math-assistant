"""RTP category registry loader."""

from __future__ import annotations

import json
from pathlib import Path

from runtime_core.domain.game_version import GameVersion


class RtpCategoryRegistry:
    def __init__(self, categories: set[str]) -> None:
        self._categories = categories

    @classmethod
    def load(cls, schema_root: Path) -> RtpCategoryRegistry:
        path = schema_root / "registries" / "rtp-categories-v1.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        categories = {item["id"] for item in doc["categories"]}
        categories.update(item["id"] for item in doc.get("aliases", []))
        return cls(categories)

    def clone(self) -> RtpCategoryRegistry:
        return RtpCategoryRegistry(set(self._categories))

    def merge_document(self, game: GameVersion) -> None:
        if game.rtp_category_registry is None:
            return
        self._categories.update(game.rtp_category_registry.categories.keys())

    def is_known(self, category: str) -> bool:
        return category in self._categories
