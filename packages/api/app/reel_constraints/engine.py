"""Reel constraint validation engine (editor-only; no runtime_core)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

ConstraintType = Literal[
    "min_count",
    "max_count",
    "exact_count",
    "min_consecutive",
    "max_consecutive",
    "min_distance",
    "forbidden_adjacency",
    "allowed_adjacency",
    "reel_specific_count",
]

ValidationStatus = Literal["pass", "warning", "error"]


class SymbolGroup(BaseModel):
    id: str
    name: str
    symbol_ids: list[str] = Field(default_factory=list, alias="symbolIds")

    model_config = {"populate_by_name": True}


class ConstraintRule(BaseModel):
    id: str
    type: ConstraintType
    enabled: bool = True
    description: str = ""
    target_type: Literal["symbol", "group"] = Field(alias="targetType")
    target_id: str = Field(alias="targetId")
    secondary_target_type: Literal["symbol", "group"] | None = Field(
        default=None, alias="secondaryTargetType"
    )
    secondary_target_id: str | None = Field(default=None, alias="secondaryTargetId")
    value: float = 0
    reel_index: int | None = Field(default=None, alias="reelIndex")
    scope: Literal["global", "per_reel"] = "global"
    severity: Literal["warning", "error"] = "error"

    model_config = {"populate_by_name": True}


class ConstraintDocument(BaseModel):
    version: Literal[1] = 1
    edge_wrapping: bool = Field(default=True, alias="edgeWrapping")
    groups: list[SymbolGroup] = Field(default_factory=list)
    inventory: dict[str, Any] = Field(default_factory=dict)
    constraints: list[ConstraintRule] = Field(default_factory=list)
    active_preset_id: str | None = Field(default=None, alias="activePresetId")

    model_config = {"populate_by_name": True}


class ValidationResultItem(BaseModel):
    constraint_id: str = Field(alias="constraintId")
    constraint_type: ConstraintType = Field(alias="constraintType")
    status: ValidationStatus
    message: str
    description: str
    expected: str
    actual: str
    affected_reels: list[int] = Field(default_factory=list, alias="affectedReels")
    affected_positions: list[dict[str, int]] = Field(
        default_factory=list, alias="affectedPositions"
    )
    suggested_fix: str | None = Field(default=None, alias="suggestedFix")
    category: str

    model_config = {"populate_by_name": True}


class ConstraintValidationReport(BaseModel):
    results: list[ValidationResultItem]
    summary: dict[str, Any]
    violations_by_position: dict[str, list[ValidationResultItem]] = Field(
        default_factory=dict, alias="violationsByPosition"
    )

    model_config = {"populate_by_name": True}


def _resolve_targets(
    target_type: str,
    target_id: str,
    groups: list[SymbolGroup],
    symbols: dict[str, Any],
) -> set[str]:
    if target_type == "symbol":
        return {target_id} if target_id in symbols else set()
    for group in groups:
        if group.id == target_id:
            return set(group.symbol_ids)
    return set()


def _matches(symbol_id: str, target_type: str, target_id: str, groups, symbols) -> bool:
    return symbol_id in _resolve_targets(target_type, target_id, groups, symbols)


def _count_in_reel(reel: dict[str, Any], target_type, target_id, groups, symbols) -> int:
    targets = _resolve_targets(target_type, target_id, groups, symbols)
    return sum(1 for item in reel.get("symbols", []) if item in targets)


def _longest_streak(reel: dict[str, Any], target_type, target_id, groups, symbols) -> int:
    longest = 0
    current = 0
    for symbol_id in reel.get("symbols", []):
        if _matches(symbol_id, target_type, target_id, groups, symbols):
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def _validate_rule(
    rule: ConstraintRule,
    reel_set: dict[str, Any],
    symbols: dict[str, Any],
    document: ConstraintDocument,
) -> ValidationResultItem:
    if not rule.enabled:
        return ValidationResultItem(
            constraintId=rule.id,
            constraintType=rule.type,
            status="pass",
            message="Constraint disabled",
            description=rule.description,
            expected="—",
            actual="—",
            category=rule.type,
        )

    reels = reel_set.get("reels", [])
    groups = document.groups
    count_global = sum(_count_in_reel(reel, rule.target_type, rule.target_id, groups, symbols) for reel in reels)

    if rule.type == "min_count":
        ok = count_global >= rule.value if rule.scope == "global" else all(
            _count_in_reel(reel, rule.target_type, rule.target_id, groups, symbols) >= rule.value
            for reel in reels
        )
        actual = str(count_global) if rule.scope == "global" else "per-reel check"
        return ValidationResultItem(
            constraintId=rule.id,
            constraintType=rule.type,
            status="pass" if ok else rule.severity,
            message="Minimum count satisfied" if ok else "Minimum count violated",
            description=rule.description,
            expected=f"≥ {rule.value}",
            actual=actual,
            category=rule.type,
        )

    if rule.type == "max_count":
        ok = count_global <= rule.value if rule.scope == "global" else all(
            _count_in_reel(reel, rule.target_type, rule.target_id, groups, symbols) <= rule.value
            for reel in reels
        )
        return ValidationResultItem(
            constraintId=rule.id,
            constraintType=rule.type,
            status="pass" if ok else rule.severity,
            message="Maximum count satisfied" if ok else "Maximum count violated",
            description=rule.description,
            expected=f"≤ {rule.value}",
            actual=str(count_global),
            category=rule.type,
        )

    if rule.type == "exact_count":
        ok = count_global == rule.value if rule.scope == "global" else all(
            _count_in_reel(reel, rule.target_type, rule.target_id, groups, symbols) == rule.value
            for reel in reels
        )
        return ValidationResultItem(
            constraintId=rule.id,
            constraintType=rule.type,
            status="pass" if ok else rule.severity,
            message="Exact count satisfied" if ok else "Exact count violated",
            description=rule.description,
            expected=f"= {rule.value}",
            actual=str(count_global),
            category=rule.type,
        )

    if rule.type == "reel_specific_count":
        reel_index = rule.reel_index or 0
        reel = next((item for item in reels if item.get("reelIndex") == reel_index), None)
        count = _count_in_reel(reel or {}, rule.target_type, rule.target_id, groups, symbols)
        ok = count == rule.value
        return ValidationResultItem(
            constraintId=rule.id,
            constraintType=rule.type,
            status="pass" if ok else rule.severity,
            message="Reel count satisfied" if ok else "Reel-specific count violated",
            description=rule.description,
            expected=f"{rule.value} on reel {reel_index + 1}",
            actual=str(count),
            affectedReels=[] if ok else [reel_index],
            category=rule.type,
        )

    if rule.type == "min_consecutive":
        longest = max(
            (_longest_streak(reel, rule.target_type, rule.target_id, groups, symbols) for reel in reels),
            default=0,
        )
        ok = longest >= rule.value
        return ValidationResultItem(
            constraintId=rule.id,
            constraintType=rule.type,
            status="pass" if ok else rule.severity,
            message="Minimum consecutive satisfied" if ok else "Minimum consecutive violated",
            description=rule.description,
            expected=f"≥ {rule.value}",
            actual=str(longest),
            category=rule.type,
        )

    if rule.type == "max_consecutive":
        worst = 0
        for reel in reels:
            current = 0
            for symbol_id in reel.get("symbols", []):
                if _matches(symbol_id, rule.target_type, rule.target_id, groups, symbols):
                    current += 1
                    worst = max(worst, current)
                else:
                    current = 0
        ok = worst <= rule.value
        return ValidationResultItem(
            constraintId=rule.id,
            constraintType=rule.type,
            status="pass" if ok else rule.severity,
            message="Maximum consecutive satisfied" if ok else "Maximum consecutive violated",
            description=rule.description,
            expected=f"≤ {rule.value}",
            actual=str(worst),
            category=rule.type,
        )

    if rule.type in {"forbidden_adjacency", "allowed_adjacency"}:
        wrap = document.edge_wrapping
        violations: list[dict[str, int]] = []
        failing_reels: list[int] = []
        secondary_type = rule.secondary_target_type or rule.target_type
        secondary_id = rule.secondary_target_id or rule.target_id
        for reel in reels:
            symbols_list = reel.get("symbols", [])
            reel_index = reel.get("reelIndex", 0)
            for index, symbol_id in enumerate(symbols_list):
                if not _matches(symbol_id, rule.target_type, rule.target_id, groups, symbols):
                    continue
                neighbors: list[int] = []
                if index > 0:
                    neighbors.append(index - 1)
                elif wrap and len(symbols_list) > 1:
                    neighbors.append(len(symbols_list) - 1)
                if index < len(symbols_list) - 1:
                    neighbors.append(index + 1)
                elif wrap and len(symbols_list) > 1:
                    neighbors.append(0)
                for neighbor_index in neighbors:
                    neighbor = symbols_list[neighbor_index]
                    secondary = _matches(neighbor, secondary_type, secondary_id, groups, symbols)
                    if rule.type == "forbidden_adjacency" and secondary:
                        failing_reels.append(reel_index)
                        violations.append({"reelIndex": reel_index, "symbolIndex": index})
                        violations.append({"reelIndex": reel_index, "symbolIndex": neighbor_index})
                    if rule.type == "allowed_adjacency" and not secondary:
                        allowed = _resolve_targets(secondary_type, secondary_id, groups, symbols)
                        if neighbor not in allowed:
                            failing_reels.append(reel_index)
                            violations.append({"reelIndex": reel_index, "symbolIndex": index})
        ok = len(violations) == 0
        label = "Forbidden adjacency" if rule.type == "forbidden_adjacency" else "Allowed adjacency"
        return ValidationResultItem(
            constraintId=rule.id,
            constraintType=rule.type,
            status="pass" if ok else rule.severity,
            message=f"{label} satisfied" if ok else f"{label} violated",
            description=rule.description,
            expected="valid neighbors",
            actual=str(len(violations) // 2),
            affectedReels=sorted(set(failing_reels)),
            affectedPositions=violations,
            category=rule.type,
        )

    if rule.type == "min_distance":
        wrap = document.edge_wrapping
        violations: list[dict[str, int]] = []
        failing_reels: list[int] = []
        worst = 999
        for reel in reels:
            symbols_list = reel.get("symbols", [])
            reel_index = reel.get("reelIndex", 0)
            indices = [
                index
                for index, symbol_id in enumerate(symbols_list)
                if _matches(symbol_id, rule.target_type, rule.target_id, groups, symbols)
            ]
            for i, a in enumerate(indices):
                for b in indices[i + 1 :]:
                    linear = abs(b - a)
                    forward = (b - a + len(symbols_list)) % len(symbols_list) if symbols_list else 0
                    backward = (a - b + len(symbols_list)) % len(symbols_list) if symbols_list else 0
                    distance = (min(linear, forward, backward) - 1) if wrap else (linear - 1)
                    if distance < rule.value:
                        worst = min(worst, distance)
                        failing_reels.append(reel_index)
                        violations.append({"reelIndex": reel_index, "symbolIndex": a})
                        violations.append({"reelIndex": reel_index, "symbolIndex": b})
        ok = len(violations) == 0
        return ValidationResultItem(
            constraintId=rule.id,
            constraintType=rule.type,
            status="pass" if ok else rule.severity,
            message="Minimum distance satisfied" if ok else "Minimum distance violated",
            description=rule.description,
            expected=f"≥ {rule.value}",
            actual="OK" if ok else str(worst),
            affectedReels=sorted(set(failing_reels)),
            affectedPositions=violations,
            category=rule.type,
        )

    return ValidationResultItem(
        constraintId=rule.id,
        constraintType=rule.type,
        status="pass",
        message="Unknown constraint",
        description=rule.description,
        expected="—",
        actual="—",
        category=rule.type,
    )


def run_constraint_engine(
    reel_set: dict[str, Any],
    symbols: dict[str, Any],
    document: ConstraintDocument,
) -> ConstraintValidationReport:
    results = [_validate_rule(rule, reel_set, symbols, document) for rule in document.constraints]
    summary = {"pass": 0, "warning": 0, "error": 0, "byCategory": {}}
    violations_by_position: dict[str, list[ValidationResultItem]] = {}
    for result in results:
        summary[result.status] += 1
        summary["byCategory"][result.category] = result.status
        if result.status != "pass":
            for position in result.affected_positions:
                key = f"{position['reelIndex']}:{position['symbolIndex']}"
                violations_by_position.setdefault(key, []).append(result)
    return ConstraintValidationReport(
        results=results,
        summary=summary,
        violationsByPosition=violations_by_position,
    )
