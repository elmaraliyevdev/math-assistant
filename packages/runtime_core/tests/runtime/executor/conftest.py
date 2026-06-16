"""SessionExecutor test helpers."""

from __future__ import annotations

from runtime_core.common.golden import load_golden_game_version
from runtime_core.domain.game_version import GameVersion
from runtime_core.golden.models import RuntimeOverrides
from runtime_core.golden.overrides import apply_runtime_overrides
from runtime_core.runtime.events import EventLogMode
from runtime_core.runtime.spin_chain import SpinChainRequest


def make_spin_chain_request(
    game: GameVersion,
    master_seed: bytes,
    *,
    spin_chain_index: int = 0,
    event_log_mode: EventLogMode = EventLogMode.REPLAY,
) -> SpinChainRequest:
    return SpinChainRequest(
        game=game,
        master_seed=master_seed,
        spin_chain_index=spin_chain_index,
        shard_index=0,
        simulation_run_id="executor-test",
        event_log_mode=event_log_mode,
    )


def relaxed_hold_and_win_game(fixture_id: str) -> GameVersion:
    """Clone a golden fixture with profile-equivalent H&W reachability overrides."""
    game = load_golden_game_version(fixture_id)
    return apply_runtime_overrides(
        game,
        RuntimeOverrides(
            hold_and_win_entry_min_count=3,
            hold_and_win_trigger_symbol_count=3,
        ),
    )
