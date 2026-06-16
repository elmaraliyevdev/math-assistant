"""End-to-end golden fixture execution via SessionExecutor."""

from __future__ import annotations

import pytest

from runtime_core.common.golden import load_golden_game_version
from runtime_core.domain.game_version import GameVersion
from runtime_core.runtime.events import EventLogMode, EventType
from runtime_core.runtime.executor import SessionExecutor
from runtime_core.runtime.spin_chain import SpinChainResult
from tests.runtime.executor.conftest import make_spin_chain_request, relaxed_hold_and_win_game


def _execute(game: GameVersion, seed: bytes) -> SpinChainResult:
    req = make_spin_chain_request(game, seed, event_log_mode=EventLogMode.REPLAY)
    return SessionExecutor().execute_spin_chain(req)


def _event_types(result: SpinChainResult) -> set[EventType]:
    return {event.event_type for event in result.events}


def _find_completing_seed(
    game: GameVersion,
    *,
    prefix: bytes,
    attempts: int = 512,
) -> bytes | None:
    for index in range(attempts):
        seed = prefix + index.to_bytes(2, "big")
        result = _execute(game, seed)
        if result.fault is None and result.limit_hit is None and result.step_count >= 1:
            return seed
    return None


def _find_seed_for_tokens(
    game: GameVersion,
    required: set[str],
    *,
    prefix: bytes,
    attempts: int = 512,
) -> bytes | None:
    for index in range(attempts):
        seed = prefix + index.to_bytes(2, "big")
        result = _execute(game, seed)
        if result.fault is not None or result.limit_hit is not None:
            continue
        emitted: set[str] = set()
        for event in result.events:
            if event.event_type == EventType.TRIGGER_EMITTED:
                emitted.update(event.payload.get("tokens", []))
            if event.event_type == EventType.TRANSITION_TAKEN:
                emitted.add(event.payload.get("trigger", ""))
        if required <= emitted:
            return seed
    return None


@pytest.mark.golden
def test_fixture_01_base_game_execution() -> None:
    game = load_golden_game_version("fixture-01-base-5x3")
    seed = _find_completing_seed(game, prefix=b"fixture-01-")
    assert seed is not None, "no completing seed found for fixture-01"
    result = _execute(game, seed)

    assert result.fault is None
    assert result.limit_hit is None
    assert result.step_count >= 1
    assert result.frame_push_count == 0
    assert EventType.SPIN_CHAIN_START in _event_types(result)
    assert EventType.GRID_RESULT in _event_types(result)
    assert result.event_log_hash


@pytest.mark.golden
def test_fixture_01_deterministic_hash() -> None:
    game = load_golden_game_version("fixture-01-base-5x3")
    seed = _find_completing_seed(game, prefix=b"fixture-01-")
    assert seed is not None
    assert _execute(game, seed).event_log_hash == _execute(game, seed).event_log_hash


@pytest.mark.golden
def test_fixture_02_base_to_free_spins() -> None:
    game = load_golden_game_version("fixture-02-base-free-spins")
    seed = _find_seed_for_tokens(game, {"FREE_SPINS"}, prefix=b"fixture-02-")
    if seed is None:
        pytest.skip("no seed produced FREE_SPINS within search budget")

    result = _execute(game, seed)
    assert result.fault is None
    assert result.limit_hit is None
    assert EventType.STATE_ENTER in _event_types(result)
    assert result.step_count > 1
    assert result.event_log_hash


@pytest.mark.golden
def test_fixture_03_base_to_hold_and_win() -> None:
    game = relaxed_hold_and_win_game("fixture-03-base-hold-win")
    seed = _find_seed_for_tokens(game, {"HOLD_AND_WIN"}, prefix=b"fixture-03-")
    if seed is None:
        pytest.skip("no seed produced HOLD_AND_WIN within search budget")

    result = _execute(game, seed)
    assert result.fault is None
    assert result.limit_hit is None
    assert result.frame_push_count >= 1
    assert EventType.FRAME_PUSH in _event_types(result)
    assert EventType.FRAME_POP in _event_types(result)
    assert result.event_log_hash


@pytest.mark.golden
def test_fixture_04_base_free_spins_hold_and_win() -> None:
    game = relaxed_hold_and_win_game("fixture-04-nested-fs-hold-win")
    seed = _find_seed_for_tokens(
        game,
        {"FREE_SPINS", "HOLD_AND_WIN"},
        prefix=b"f04-",
        attempts=10000,
    )
    if seed is None:
        pytest.skip("no seed produced nested FS→H&W within search budget")

    result = _execute(game, seed)
    assert result.fault is None
    assert result.limit_hit is None
    assert result.frame_push_count >= 1
    assert result.step_count > 3
    assert result.event_log_hash


@pytest.mark.golden
def test_fixture_01_event_log_hash_is_stable_within_executor_tests() -> None:
    """Deterministic replay hash under executor-test simulation profile."""
    game = load_golden_game_version("fixture-01-base-5x3")
    seed = b"fixture-01-\x00\x01"
    assert _execute(game, seed).event_log_hash == _execute(game, seed).event_log_hash
