"""Session resolution and context tests."""

from __future__ import annotations

import pytest
from tests.runtime.conftest import session_test_game

from runtime_core.domain.game_version import GameVersion
from runtime_core.runtime.events import EventLogMode
from runtime_core.runtime.exceptions import RNGError
from runtime_core.runtime.rng import RNGServiceConfig
from runtime_core.runtime.session import (
    NewSessionParams,
    content_hash,
    new_session_context,
    new_session_params_from_request,
    resolve_bet,
    resolve_exposure,
    resolve_limits,
    validate_determinism,
)
from runtime_core.runtime.spin_chain import SpinChainRequest
from runtime_core.runtime.version import ENGINE_VERSION


def valid_params() -> NewSessionParams:
    return NewSessionParams(
        game=session_test_game(),
        engine_version=ENGINE_VERSION,
        master_seed=b"seed",
        spin_chain_index=1,
        shard_index=0,
        simulation_run_id="sim-run",
    )


def test_new_session_success() -> None:
    ctx = new_session_context(valid_params())
    assert ctx.game_version_content_hash == "fixed-content-hash"
    assert ctx.total_bet_minor_units == 4000
    assert ctx.inheritance_policy == "mvp-v1"
    assert ctx.limits.max_steps_per_spin_chain == 100
    assert ctx.limits.max_frames_per_chain == 6
    assert ctx.exposure.effective_cap_minor == 10000


def test_new_session_required_fields() -> None:
    params = valid_params()
    with pytest.raises(ValueError, match="engineVersion"):
        new_session_context(
            NewSessionParams(
                game=params.game,
                engine_version="",
                master_seed=params.master_seed,
                spin_chain_index=0,
                shard_index=0,
                simulation_run_id="r",
            ),
        )
    with pytest.raises(ValueError, match="masterSeed"):
        new_session_context(
            NewSessionParams(
                game=params.game,
                engine_version="e",
                master_seed=b"",
                spin_chain_index=0,
                shard_index=0,
                simulation_run_id="r",
            ),
        )
    with pytest.raises(ValueError, match="simulationRunID"):
        new_session_context(
            NewSessionParams(
                game=params.game,
                engine_version="e",
                master_seed=b"s",
                spin_chain_index=0,
                shard_index=0,
                simulation_run_id="",
            ),
        )


def test_resolve_bet_override() -> None:
    params = valid_params()
    params = NewSessionParams(
        game=params.game,
        engine_version=params.engine_version,
        master_seed=params.master_seed,
        spin_chain_index=params.spin_chain_index,
        shard_index=params.shard_index,
        simulation_run_id=params.simulation_run_id,
        bet_minor_units=777,
    )
    ctx = new_session_context(params)
    assert ctx.total_bet_minor_units == 777
    assert ctx.bet.total_bet_minor_units == 777


def test_resolve_bet_total_bet_minor_units_field() -> None:
    game = session_test_game()
    payload = game.to_json_dict()
    payload["betModel"]["totalBetMinorUnits"] = 2500
    game = GameVersion.model_validate(payload)
    _, total = resolve_bet(game, 0)
    assert total == 2500


def test_resolve_bet_defaults_lines_to_one() -> None:
    game = session_test_game()
    payload = game.to_json_dict()
    payload["betModel"]["lineCount"] = 0
    payload["betModel"]["coinValueScale"] = 0
    payload["betModel"]["defaultCoinValue"] = 0
    game = GameVersion.model_validate(payload)
    _, total = resolve_bet(game, 0)
    assert total == 1


def test_validate_determinism() -> None:
    game = session_test_game()
    payload = game.to_json_dict()
    payload["determinism"]["rngAlgorithm"] = "MT19937"
    with pytest.raises(ValueError, match="rngAlgorithm"):
        validate_determinism(GameVersion.model_validate(payload))

    payload = game.to_json_dict()
    payload["determinism"]["seedDerivationPolicy"] = "legacy"
    with pytest.raises(ValueError, match="seedDerivationPolicy"):
        validate_determinism(GameVersion.model_validate(payload))

    payload = game.to_json_dict()
    payload["determinism"]["moneyRepresentation"] = "float"
    with pytest.raises(ValueError, match="moneyRepresentation"):
        validate_determinism(GameVersion.model_validate(payload))


def test_content_hash_computed_when_missing() -> None:
    game = session_test_game()
    payload = game.to_json_dict()
    payload.pop("contentHash", None)
    game = GameVersion.model_validate(payload)
    digest = content_hash(game)
    assert len(digest) == 64


def test_platform_limits_defaults() -> None:
    game = session_test_game()
    payload = game.to_json_dict()
    payload["session"]["runtimeLimits"] = None
    payload["session"]["maxStackDepth"] = 0
    game = GameVersion.model_validate(payload)
    limits = resolve_limits(game)
    assert limits.max_steps_per_spin_chain == 500
    assert limits.max_frames_per_chain == 8


def test_exposure_cap_uses_multiplier_when_smaller() -> None:
    game = session_test_game()
    exposure = resolve_exposure(game, 4000)
    assert exposure.effective_cap_minor == 10000

    payload = game.to_json_dict()
    payload["exposure"]["maxWinMinorUnits"] = 500000
    game = GameVersion.model_validate(payload)
    exposure = resolve_exposure(game, 4000)
    assert exposure.effective_cap_minor == 400000


def test_exposure_cap_uses_max_win_when_smaller() -> None:
    game = session_test_game()
    payload = game.to_json_dict()
    payload["exposure"]["maxWinMultiplier"] = 0
    payload["exposure"]["maxWinMinorUnits"] = 500
    game = GameVersion.model_validate(payload)
    exposure = resolve_exposure(game, 4000)
    assert exposure.effective_cap_minor == 500


def test_resolve_limits_overrides_all_fields() -> None:
    game = session_test_game()
    payload = game.to_json_dict()
    payload["session"]["runtimeLimits"] = {
        "maxStepsPerSpinChain": 1,
        "maxFramesPerChain": 2,
        "maxTransitionsPerStep": 3,
        "maxRespinsPerFeature": 4,
        "maxEventsPerChain": 5,
        "maxWallClockMsPerChain": 6,
    }
    payload["session"]["maxStackDepth"] = 10
    game = GameVersion.model_validate(payload)
    limits = resolve_limits(game)
    assert limits.max_steps_per_spin_chain == 1
    assert limits.max_frames_per_chain == 2
    assert limits.max_transitions_per_step == 3
    assert limits.max_respins_per_feature == 4
    assert limits.max_events_per_chain == 5
    assert limits.max_wall_clock_ms_per_chain == 6


def test_default_inheritance_policy() -> None:
    game = session_test_game()
    payload = game.to_json_dict()
    payload["session"]["contextInheritancePolicy"] = None
    game = GameVersion.model_validate(payload)
    ctx = new_session_context(
        NewSessionParams(
            game=game,
            engine_version="e",
            master_seed=b"s",
            spin_chain_index=0,
            shard_index=0,
            simulation_run_id="r",
        ),
    )
    assert ctx.inheritance_policy == "mvp-v1"


def test_new_session_context_rng_error() -> None:
    params = valid_params()
    params = NewSessionParams(
        game=params.game,
        engine_version=params.engine_version,
        master_seed=params.master_seed,
        spin_chain_index=params.spin_chain_index,
        shard_index=params.shard_index,
        simulation_run_id=params.simulation_run_id,
        rng_config=RNGServiceConfig(algorithm="bad"),
    )
    with pytest.raises(RNGError):
        new_session_context(params)


def test_resolve_limits_ignores_zero_overrides() -> None:
    game = session_test_game()
    payload = game.to_json_dict()
    payload["session"]["runtimeLimits"] = {
        "maxStepsPerSpinChain": 0,
        "maxFramesPerChain": 0,
    }
    game = GameVersion.model_validate(payload)
    limits = resolve_limits(game)
    assert limits.max_steps_per_spin_chain == 500
    assert limits.max_frames_per_chain == 6


def test_new_session_params_from_request() -> None:
    game = session_test_game()
    req = SpinChainRequest(
        game=game,
        master_seed=b"seed",
        spinChainIndex=2,
        shardIndex=1,
        simulationRunId="run",
        betMinorUnits=50,
        eventLogMode=EventLogMode.FULL,
    )
    params = new_session_params_from_request(req)
    assert params.spin_chain_index == 2
    assert params.engine_version == ENGINE_VERSION
    ctx = new_session_context(params)
    assert ctx.total_bet_minor_units == 50
    assert ctx.events.mode == EventLogMode.FULL
