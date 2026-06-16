"""Plugin config cross-reference validation."""

from __future__ import annotations

from typing import Any

from runtime_core.domain.game_version import GameVersion
from runtime_core.validation.validators.finding import Finding, err_finding


def validate_plugin_references(game: GameVersion | None) -> list[Finding]:
    findings: list[Finding] = []
    if game is None:
        return findings
    for machine_id, machine in game.state_machines.items():
        for state_id, state in machine.states.items():
            base_path = f"stateMachines.{machine_id}.states.{state_id}.pluginConfig"
            findings.extend(_validate_symbol_refs(game, base_path, state.plugin_config))
            findings.extend(_validate_reel_set(game, base_path, state.plugin_config))
    return findings


def _validate_symbol_refs(
    game: GameVersion,
    base_path: str,
    config: dict[str, Any],
) -> list[Finding]:
    findings: list[Finding] = []
    if not config:
        return findings

    def check_symbol(field: str, symbol_id: str) -> None:
        if symbol_id and symbol_id not in game.symbols:
            findings.append(
                err_finding(
                    "GV-021",
                    f"{base_path}.{field}",
                    f"symbol '{symbol_id}' referenced in plugin config does not exist",
                    "Define the symbol in symbols or fix the reference",
                ),
            )

    reel_set_id = config.get("reelSetId")
    if isinstance(reel_set_id, str) and reel_set_id not in game.reel_sets:
        findings.append(
            err_finding(
                "GV-021",
                f"{base_path}.reelSetId",
                f"symbol '{reel_set_id}' referenced in plugin config does not exist",
                "Define the symbol in symbols or fix the reference",
            ),
        )
    trigger_symbol = config.get("triggerSymbolId")
    if isinstance(trigger_symbol, str):
        check_symbol("triggerSymbolId", trigger_symbol)
    multiplier_ref = config.get("multiplierRefId")
    if isinstance(multiplier_ref, str) and multiplier_ref not in game.plugins:
        findings.append(
            err_finding(
                "GV-018",
                f"{base_path}.multiplierRefId",
                f"pluginRefId '{multiplier_ref}' does not exist in plugins registry",
                "Define the plugin reference or fix pluginRefId",
            ),
        )
    for field in ("scatterTriggers", "bonusTriggers"):
        triggers = config.get(field)
        if not isinstance(triggers, list):
            continue
        for index, item in enumerate(triggers):
            if not isinstance(item, dict):
                continue
            symbol_id = item.get("symbolId")
            if isinstance(symbol_id, str):
                check_symbol(f"{field}[{index}].symbolId", symbol_id)
    return findings


def _validate_reel_set(
    game: GameVersion,
    base_path: str,
    config: dict[str, Any],
) -> list[Finding]:
    reel_set_id = config.get("reelSetId") if config else None
    if not isinstance(reel_set_id, str) or not reel_set_id:
        return []
    reel_set = game.reel_sets.get(reel_set_id)
    if reel_set is None:
        return []
    expected = game.game_config.grid.reels
    actual = len(reel_set.reels)
    if expected > 0 and actual != expected:
        return [
            err_finding(
                "GV-022",
                f"{base_path}.reelSetId",
                "reel set reel count does not match game grid",
                f"Ensure reel set has {expected} reels (found {actual})",
            ),
        ]
    return []
