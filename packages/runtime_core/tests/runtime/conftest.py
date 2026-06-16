"""Runtime test fixtures."""

from __future__ import annotations

import pytest

from runtime_core.common.golden import load_golden_game_version
from runtime_core.common.paths import game_schema_root
from runtime_core.domain.game_version import GameVersion
from runtime_core.validation.validators.priority_tiers import PriorityTierRegistry


@pytest.fixture(scope="session")
def priority_tiers() -> PriorityTierRegistry:
    return PriorityTierRegistry.load(game_schema_root())


@pytest.fixture(scope="session")
def base_game() -> GameVersion:
    return load_golden_game_version("fixture-01-base-5x3")


@pytest.fixture(scope="session")
def nested_game() -> GameVersion:
    return load_golden_game_version("fixture-04-nested-fs-hold-win")


def session_test_game() -> GameVersion:
    return GameVersion.model_validate(
        {
            "schemaVersion": "1.0.0",
            "contentHash": "fixed-content-hash",
            "gameVersion": {
                "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "projectId": "f0e1d2c3-b4a5-9678-9012-3456789abcde",
                "versionNumber": 1,
                "status": "draft",
                "createdAt": "2026-06-14T10:00:00Z",
            },
            "metadata": {"title": "Session Test Game"},
            "gameConfig": {
                "grid": {"reels": 5, "rows": 3},
                "defaultReelSetId": "base",
            },
            "symbols": {"H1": {"id": "H1", "type": "regular"}},
            "reelSets": {
                "base": {
                    "id": "base",
                    "reels": [{"reelIndex": 0, "symbols": ["H1"]}],
                },
            },
            "paytable": {
                "lines": [{"index": 1, "path": [0, 0, 0, 0, 0]}],
                "pays": [{"symbolId": "H1", "count": 3, "multiplier": 10}],
            },
            "winModel": {"type": "lines", "direction": "left-to-right"},
            "betModel": {
                "type": "lines",
                "lineCount": 20,
                "coinValueScale": 100,
                "defaultCoinValue": 2,
            },
            "plugins": {
                "base": {
                    "refId": "base",
                    "pluginId": "core.base-game",
                    "pluginVersion": "1.0.0",
                    "configSchemaVersion": "1.0.0",
                    "capabilities": ["spin.grid"],
                },
            },
            "stateMachines": {
                "main": {
                    "id": "main",
                    "initialStateId": "BASE",
                    "states": {
                        "BASE": {
                            "id": "BASE",
                            "pluginRefId": "base",
                            "stateType": "atomic_spin",
                            "rtpCategory": "BASE",
                            "pluginConfig": {"reelSetId": "base"},
                            "transitions": [
                                {
                                    "id": "t1",
                                    "trigger": "SPIN_COMPLETE",
                                    "priorityTier": "FALLBACK",
                                    "priority": 1000,
                                    "effect": "stay",
                                    "targetStateId": "BASE",
                                },
                            ],
                        },
                    },
                },
            },
            "session": {
                "rootMachineId": "main",
                "maxStackDepth": 6,
                "spinLoopMode": "single_chain",
                "contextInheritancePolicy": "mvp-v1",
                "runtimeLimits": {
                    "maxStepsPerSpinChain": 100,
                    "maxEventsPerChain": 500,
                },
            },
            "exposure": {
                "maxWinMinorUnits": 10000,
                "maxWinMultiplier": 100,
                "capScope": "session_spin_chain",
                "enforceCap": True,
                "validationMode": "strict",
            },
            "determinism": {
                "rngAlgorithm": "PCG64",
                "seedDerivationPolicy": "v1-hash-shard",
                "moneyRepresentation": "fixed_minor_units",
            },
            "precedence": {"triggerOrder": ["SPIN_COMPLETE"]},
            "extensions": {},
        },
    )
