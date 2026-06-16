"""Shared fixtures for validation API tests."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import pytest
from runtime_core.common.golden import load_golden_fixture_json

from app.adapters.game_version import compute_content_hash


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


@pytest.fixture(scope="session")
def valid_canonical_json() -> dict[str, Any]:
    return load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())


@pytest.fixture
def invalid_canonical_json(valid_canonical_json: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(valid_canonical_json)
    payload["stateMachines"]["main"]["states"]["BASE"]["transitions"].append(
        {
            "id": "t_bad",
            "trigger": "SPIN_COMPLETE",
            "priorityTier": "FALLBACK",
            "priority": 1000,
            "effect": "goto",
            "targetStateId": "MISSING",
        },
    )
    return payload


@pytest.fixture
def expected_content_hash(valid_canonical_json: dict[str, Any]) -> str:
    return compute_content_hash(valid_canonical_json)
