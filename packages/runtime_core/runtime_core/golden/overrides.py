"""Apply golden runtime profile overrides to a canonical GameVersion."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.golden.models import RuntimeOverrides


def apply_runtime_overrides(
    game: GameVersion,
    overrides: RuntimeOverrides | None,
) -> GameVersion:
    """Return a copy of *game* with optional H&W reachability overrides applied."""
    if overrides is None:
        return game
    if (
        overrides.hold_and_win_entry_min_count is None
        and overrides.hold_and_win_trigger_symbol_count is None
    ):
        return game

    payload = game.to_json_dict()
    min_count = overrides.hold_and_win_entry_min_count
    if min_count is not None:
        main_states = payload["stateMachines"]["main"]["states"]
        for state_id in ("BASE", "FREE_SPINS"):
            state = main_states.get(state_id)
            if state is None:
                continue
            for trigger in state.get("pluginConfig", {}).get("bonusTriggers", []):
                trigger["minCount"] = min_count

    trigger_count = overrides.hold_and_win_trigger_symbol_count
    haw_machine = payload["stateMachines"].get("hold_and_win")
    if trigger_count is not None and haw_machine is not None:
        haw_state = haw_machine["states"].get("HAW_RESPINS")
        if haw_state is not None:
            haw_state["pluginConfig"]["triggerSymbolCount"] = trigger_count

    return GameVersion.model_validate(payload)
