"""Multiplier orchestration for SessionExecutor."""

from __future__ import annotations

from typing import Any

from runtime_core.domain.game_version import GameVersion
from runtime_core.runtime.rng import FrameStream
from runtime_core.runtime.session.factory import SessionContext


def resolve_multiplier_config(
    game: GameVersion,
    multiplier_ref_id: str,
) -> dict[str, Any] | None:
    configs = game.extensions.get("multiplierConfigs")
    if isinstance(configs, dict):
        raw = configs.get(multiplier_ref_id)
        if isinstance(raw, dict):
            return dict(raw)
    return None


def apply_frame_multiplier(
    game: GameVersion,
    session: SessionContext,
    *,
    multiplier_ref_id: str,
    wins: list[dict[str, Any]],
    frame_stream: FrameStream,
    apply_index: int,
) -> tuple[list[dict[str, Any]], int | None]:
    """Apply configured multiplier to wins; returns adjusted wins and factor."""
    from runtime_core.plugins.multiplier.plugin import MultiplierPlugin

    config = resolve_multiplier_config(game, multiplier_ref_id)
    if config is None or not wins:
        return wins, None
    rng = frame_stream.multiplier_rng(multiplier_ref_id, apply_index)
    plugin = MultiplierPlugin()
    result = plugin.apply_wins(config, [dict(win) for win in wins], rng)
    factor = result.frame_local_patch.get("multiplierFactor")
    return result.wins, int(factor) if factor is not None else None
