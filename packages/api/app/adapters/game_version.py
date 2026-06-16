"""Canonical game JSON adapters — public runtime_core domain APIs only."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from runtime_core.domain import GameVersion


def compute_content_hash(canonical_json: dict[str, Any]) -> str:
    """Deterministic SHA-256 hash of canonical game JSON."""
    payload = json.dumps(
        canonical_json,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def parse_game_version(canonical_json: dict[str, Any]) -> GameVersion:
    """Parse canonical JSON into a :class:`GameVersion`."""
    return GameVersion.model_validate(canonical_json)
