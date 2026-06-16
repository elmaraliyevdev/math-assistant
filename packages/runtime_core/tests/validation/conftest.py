"""Shared validation test fixtures and game builders."""

from __future__ import annotations

import pytest

from runtime_core.domain.game_version import GameVersion
from runtime_core.validation.engine import ValidationEngine


@pytest.fixture(scope="session")
def validation_engine() -> ValidationEngine:
    return ValidationEngine.create()


def build_valid_base_game() -> GameVersion:
    return GameVersion.model_validate(
        {
            "schemaVersion": "1.0.0",
            "gameVersion": {
                "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "projectId": "f0e1d2c3-b4a5-9678-9012-3456789abcde",
                "versionNumber": 1,
                "status": "draft",
                "createdAt": "2026-06-14T10:00:00Z",
                "source": "dsl-compiler",
                "label": "Valid Base Game",
            },
            "metadata": {
                "title": "Base 5x3",
                "rtpTarget": {"percent": 96.0, "tolerance": 0.1},
            },
            "gameConfig": {
                "grid": {"reels": 5, "rows": 3, "indexOrigin": "top-left"},
                "defaultReelSetId": "base_game",
            },
            "symbols": {
                "H1": {"id": "H1", "type": "regular", "displayName": "High 1"},
                "L1": {"id": "L1", "type": "regular", "displayName": "Low 1"},
                "SCATTER": {"id": "SCATTER", "type": "scatter", "pays": False},
            },
            "reelSets": {
                "base_game": {
                    "id": "base_game",
                    "reels": [
                        {
                            "reelIndex": i,
                            "symbols": ["L1", "H1", "SCATTER", "L1", "H1"],
                        }
                        for i in range(5)
                    ],
                },
            },
            "paytable": {
                "lines": [{"index": 1, "path": [1, 1, 1, 1, 1]}],
                "pays": [{"symbolId": "H1", "count": 5, "multiplier": 100}],
            },
            "winModel": {
                "type": "lines",
                "direction": "left-to-right",
                "scatterPaysOnReels": True,
                "highestWinOnlyPerLine": True,
            },
            "betModel": {
                "type": "lines",
                "lineCount": 20,
                "coinValueScale": 100,
                "defaultCoinValue": 1,
                "minCoinValue": 1,
                "maxCoinValue": 1,
            },
            "plugins": {
                "base_main": {
                    "refId": "base_main",
                    "pluginId": "core.base-game",
                    "pluginVersion": "1.0.0",
                    "configSchemaVersion": "1.0.0",
                    "capabilities": ["spin.grid", "win.lines", "win.scatter"],
                },
            },
            "stateMachines": {
                "main": {
                    "id": "main",
                    "initialStateId": "BASE",
                    "states": {
                        "BASE": {
                            "id": "BASE",
                            "pluginRefId": "base_main",
                            "stateType": "atomic_spin",
                            "rtpCategory": "BASE",
                            "pluginConfig": {
                                "reelSetId": "base_game",
                                "scatterTriggers": [
                                    {
                                        "symbolId": "SCATTER",
                                        "minCount": 3,
                                        "emitTrigger": "FREE_SPINS",
                                    },
                                ],
                            },
                            "transitions": [
                                {
                                    "id": "t_spin",
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
                "maxStackDepth": 4,
                "spinLoopMode": "single_chain",
                "contextInheritancePolicy": "mvp-v1",
                "runtimeLimits": {"maxStepsPerSpinChain": 500},
            },
            "exposure": {
                "maxWinMinorUnits": 500000,
                "maxWinMultiplier": 5000,
                "capScope": "session_spin_chain",
                "enforceCap": True,
                "validationMode": "strict",
            },
            "determinism": {
                "rngAlgorithm": "PCG64",
                "rngAlgorithmVersion": "1.0",
                "seedDerivationPolicy": "v1-hash-shard",
                "moneyRepresentation": "fixed_minor_units",
                "moneyScale": 10000,
            },
            "precedence": {"triggerOrder": ["SPIN_COMPLETE"]},
            "extensions": {},
        },
    )


def build_nested_fs_haw() -> GameVersion:
    base = build_valid_base_game()
    payload = base.to_json_dict()
    payload["gameVersion"]["label"] = "Golden Fixture 4 — Nested FS + H&W"
    payload["metadata"]["title"] = "Example Nested Slot"
    payload["symbols"].update(
        {
            "H2": {"id": "H2", "type": "regular", "displayName": "High 2"},
            "L2": {"id": "L2", "type": "regular", "displayName": "Low 2"},
            "WILD": {
                "id": "WILD",
                "type": "wild",
                "substitutes": ["H1", "H2", "L1", "L2"],
            },
            "BONUS": {"id": "BONUS", "type": "bonus", "pays": False},
        },
    )
    payload["reelSets"]["free_spins"] = {
        "id": "free_spins",
        "reels": [
            {
                "reelIndex": i,
                "symbols": ["L1", "H1", "SCATTER", "H1", "BONUS"],
            }
            for i in range(5)
        ],
    }
    payload["reelSets"]["hold_and_win"] = {
        "id": "hold_and_win",
        "reels": [
            {
                "reelIndex": i,
                "symbols": ["BONUS", "L1", "BONUS", "L2", "BONUS"],
            }
            for i in range(5)
        ],
    }
    payload["plugins"].update(
        {
            "fs_main": {
                "refId": "fs_main",
                "pluginId": "core.free-spins",
                "pluginVersion": "1.0.0",
                "configSchemaVersion": "1.0.0",
                "capabilities": [
                    "spin.grid",
                    "win.lines",
                    "win.scatter",
                    "feature.retrigger",
                    "feature.nested",
                ],
            },
            "haw_main": {
                "refId": "haw_main",
                "pluginId": "core.hold-and-win",
                "pluginVersion": "1.0.0",
                "configSchemaVersion": "1.0.0",
                "capabilities": ["spin.grid", "state.multistep", "jackpot.local"],
            },
            "mult_fs": {
                "refId": "mult_fs",
                "pluginId": "core.multiplier",
                "pluginVersion": "1.0.0",
                "configSchemaVersion": "1.0.0",
                "capabilities": ["multiplier.apply"],
            },
            "mult_haw": {
                "refId": "mult_haw",
                "pluginId": "core.multiplier",
                "pluginVersion": "1.0.0",
                "configSchemaVersion": "1.0.0",
                "capabilities": ["multiplier.apply"],
            },
        },
    )
    payload["stateMachines"]["main"]["states"]["BASE"] = {
        "id": "BASE",
        "pluginRefId": "base_main",
        "stateType": "atomic_spin",
        "rtpCategory": "BASE",
        "pluginConfig": {
            "reelSetId": "base_game",
            "scatterTriggers": [
                {"symbolId": "SCATTER", "minCount": 3, "emitTrigger": "FREE_SPINS"},
            ],
            "bonusTriggers": [
                {"symbolId": "BONUS", "minCount": 6, "emitTrigger": "HOLD_AND_WIN"},
            ],
        },
        "transitions": [
            {
                "id": "t_base_to_fs",
                "trigger": "FREE_SPINS",
                "priorityTier": "FEATURE_ENTRY",
                "priority": 200,
                "effect": "goto",
                "targetStateId": "FREE_SPINS",
            },
            {
                "id": "t_base_to_haw",
                "trigger": "HOLD_AND_WIN",
                "priorityTier": "FEATURE_ENTRY_SPAWN",
                "priority": 100,
                "effect": "spawn",
                "targetMachineId": "hold_and_win",
            },
            {
                "id": "t_base_spin",
                "trigger": "SPIN_COMPLETE",
                "priorityTier": "FALLBACK",
                "priority": 1000,
                "effect": "stay",
                "targetStateId": "BASE",
            },
        ],
    }
    payload["stateMachines"]["main"]["states"]["FREE_SPINS"] = {
        "id": "FREE_SPINS",
        "pluginRefId": "fs_main",
        "stateType": "atomic_spin",
        "rtpCategory": "FREE_SPINS",
        "pluginConfig": {
            "reelSetId": "free_spins",
            "awardsByScatterCount": {"3": 10, "4": 15, "5": 20},
            "retrigger": {
                "enabled": True,
                "awardsByScatterCount": {"3": 5, "4": 10, "5": 15},
            },
            "multiplierRefId": "mult_fs",
            "bonusTriggers": [
                {"symbolId": "BONUS", "minCount": 6, "emitTrigger": "HOLD_AND_WIN"},
            ],
        },
        "transitions": [
            {
                "id": "t_fs_to_haw",
                "trigger": "HOLD_AND_WIN",
                "priorityTier": "FEATURE_ENTRY_SPAWN",
                "priority": 100,
                "effect": "spawn",
                "targetMachineId": "hold_and_win",
            },
            {
                "id": "t_fs_complete",
                "trigger": "FEATURE_COMPLETE",
                "priorityTier": "FEATURE_EXIT",
                "priority": 900,
                "effect": "goto",
                "targetStateId": "BASE",
            },
        ],
    }
    payload["stateMachines"]["hold_and_win"] = {
        "id": "hold_and_win",
        "initialStateId": "HAW_RESPINS",
        "states": {
            "HAW_RESPINS": {
                "id": "HAW_RESPINS",
                "pluginRefId": "haw_main",
                "stateType": "multi_step",
                "rtpCategory": "HOLD_AND_WIN",
                "pluginConfig": {
                    "reelSetId": "hold_and_win",
                    "triggerSymbolId": "BONUS",
                    "triggerSymbolCount": 6,
                    "initialRespins": 3,
                    "gridCapacity": 15,
                    "jackpotTiers": {"mini": 20, "major": 100, "grand": 500},
                    "multiplierRefId": "mult_haw",
                },
                "progression": {
                    "counterField": "respinsRemaining",
                    "decrementsOn": "each_step",
                    "minValue": 0,
                    "terminatesWhen": "respinsRemaining == 0 OR gridFull == true",
                },
                "transitions": [
                    {
                        "id": "t_haw_pop",
                        "trigger": "FEATURE_COMPLETE",
                        "priorityTier": "FEATURE_EXIT",
                        "priority": 900,
                        "effect": "pop",
                    },
                ],
            },
        },
    }
    payload["session"]["maxStackDepth"] = 4
    payload["session"]["runtimeLimits"] = {
        "maxStepsPerSpinChain": 500,
        "maxRespinsPerFeature": 100,
    }
    payload["exposure"] = {
        "maxWinMinorUnits": 1200000,
        "maxWinMultiplier": 5000,
        "capScope": "session_spin_chain",
        "enforceCap": True,
        "validationMode": "strict",
    }
    payload["precedence"] = {
        "triggerOrder": [
            "HOLD_AND_WIN",
            "FREE_SPINS",
            "FEATURE_COMPLETE",
            "SPIN_COMPLETE",
        ],
    }
    payload["rtpCategoryRegistry"] = {
        "extends": "platform:v1",
        "categories": {
            "BASE": {"label": "Base Game", "decompositionGroup": "base"},
            "FREE_SPINS": {"label": "Free Spins", "decompositionGroup": "feature"},
            "HOLD_AND_WIN": {"label": "Hold and Win", "decompositionGroup": "feature"},
        },
    }
    return GameVersion.model_validate(payload)
