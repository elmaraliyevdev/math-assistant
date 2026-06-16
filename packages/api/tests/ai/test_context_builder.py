"""Context builder tests."""

from __future__ import annotations

from app.ai.context_builder import (
    extract_jackpot_tiers,
    extract_paytable_summary,
    extract_rtp_target,
    extract_scatter_triggers,
)


def test_extract_rtp_target(valid_canonical_json: dict) -> None:
    assert extract_rtp_target(valid_canonical_json) == 96.0


def test_extract_scatter_triggers(valid_canonical_json: dict) -> None:
    triggers = extract_scatter_triggers(valid_canonical_json)
    assert triggers
    assert triggers[0]["emitTrigger"] == "FREE_SPINS"


def test_extract_paytable_summary(valid_canonical_json: dict) -> None:
    pays = extract_paytable_summary(valid_canonical_json)
    assert pays[0]["symbolId"] == "H1"


def test_extract_jackpot_tiers_empty(valid_canonical_json: dict) -> None:
    assert extract_jackpot_tiers(valid_canonical_json) == {}
