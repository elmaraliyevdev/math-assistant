import type {
  ConstraintEngineInput,
  ConstraintRule,
  ConstraintValidationReport,
  ValidationResultItem,
  ValidationStatus,
} from '@/features/reel-studio/constraints/types'
import { positionKey } from '@/features/reel-studio/constraints/types'
import {
  circularDistance,
  countSymbolsGlobal,
  countSymbolsInReel,
  findStreakViolations,
  getAdjacentIndices,
  longestStreak,
  resolveTargetSymbolIds,
  symbolMatches,
} from '@/features/reel-studio/constraints/engine/utils'
import type { StudioReelStrip } from '@/features/reel-studio/types'

export type ConstraintValidator = (
  rule: ConstraintRule,
  input: ConstraintEngineInput,
) => ValidationResultItem

function baseResult(
  rule: ConstraintRule,
  status: ValidationStatus,
  message: string,
  expected: string,
  actual: string,
  affectedReels: number[],
  affectedPositions: ValidationResultItem['affectedPositions'],
  suggestedFix?: string,
): ValidationResultItem {
  return {
    constraintId: rule.id,
    constraintType: rule.type,
    status,
    message,
    description: rule.description,
    expected,
    actual,
    affectedReels,
    affectedPositions,
    suggestedFix,
    category: rule.type,
  }
}

function validateMinCount(rule: ConstraintRule, input: ConstraintEngineInput): ValidationResultItem {
  const { reelSet, symbols, constraintDocument } = input
  const { groups } = constraintDocument
  if (rule.scope === 'per_reel') {
    const failingReels: number[] = []
    for (const reel of reelSet.reels) {
      const count = countSymbolsInReel(reel, rule.targetType, rule.targetId, groups, symbols)
      if (count < rule.value) {
        failingReels.push(reel.reelIndex)
      }
    }
    const actual = failingReels.length
      ? `Reels ${failingReels.map((r) => r + 1).join(', ')} below minimum`
      : 'All reels satisfy minimum'
    const status: ValidationStatus = failingReels.length ? rule.severity : 'pass'
    return baseResult(
      rule,
      status,
      status === 'pass' ? 'Minimum count satisfied' : 'Minimum count violated',
      `≥ ${rule.value} per reel`,
      actual,
      failingReels,
      [],
      `Add symbols until each reel has at least ${rule.value}.`,
    )
  }
  const count = countSymbolsGlobal(reelSet.reels, rule.targetType, rule.targetId, groups, symbols)
  const status: ValidationStatus = count >= rule.value ? 'pass' : rule.severity
  return baseResult(
    rule,
    status,
    status === 'pass' ? 'Minimum count satisfied' : 'Minimum count violated',
    `≥ ${rule.value}`,
    String(count),
    status === 'pass' ? [] : reelSet.reels.map((reel) => reel.reelIndex),
    [],
    `Add ${rule.value - count} more symbol(s) across reels.`,
  )
}

function validateMaxCount(rule: ConstraintRule, input: ConstraintEngineInput): ValidationResultItem {
  const { reelSet, symbols, constraintDocument } = input
  const { groups } = constraintDocument
  if (rule.scope === 'per_reel') {
    const failingReels: number[] = []
    const positions: ValidationResultItem['affectedPositions'] = []
    for (const reel of reelSet.reels) {
      const count = countSymbolsInReel(reel, rule.targetType, rule.targetId, groups, symbols)
      if (count > rule.value) {
        failingReels.push(reel.reelIndex)
        reel.symbols.forEach((symbolId, symbolIndex) => {
          if (symbolMatches(symbolId, rule.targetType, rule.targetId, groups, symbols)) {
            positions.push({ reelIndex: reel.reelIndex, symbolIndex })
          }
        })
      }
    }
    const status: ValidationStatus = failingReels.length ? rule.severity : 'pass'
    return baseResult(
      rule,
      status,
      status === 'pass' ? 'Maximum count satisfied' : 'Maximum count violated',
      `≤ ${rule.value} per reel`,
      failingReels.length ? `Reels ${failingReels.map((r) => r + 1).join(', ')} exceed max` : 'OK',
      failingReels,
      positions,
      `Remove excess symbols to stay at or below ${rule.value} per reel.`,
    )
  }
  const count = countSymbolsGlobal(reelSet.reels, rule.targetType, rule.targetId, groups, symbols)
  const status: ValidationStatus = count <= rule.value ? 'pass' : rule.severity
  const positions: ValidationResultItem['affectedPositions'] = []
  if (status !== 'pass') {
    for (const reel of reelSet.reels) {
      reel.symbols.forEach((symbolId, symbolIndex) => {
        if (symbolMatches(symbolId, rule.targetType, rule.targetId, groups, symbols)) {
          positions.push({ reelIndex: reel.reelIndex, symbolIndex })
        }
      })
    }
  }
  return baseResult(
    rule,
    status,
    status === 'pass' ? 'Maximum count satisfied' : 'Maximum count violated',
    `≤ ${rule.value}`,
    String(count),
    status === 'pass' ? [] : reelSet.reels.map((reel) => reel.reelIndex),
    positions,
    `Remove ${count - rule.value} symbol(s).`,
  )
}

function validateExactCount(rule: ConstraintRule, input: ConstraintEngineInput): ValidationResultItem {
  const { reelSet, symbols, constraintDocument } = input
  const { groups } = constraintDocument
  if (rule.scope === 'per_reel') {
    const failingReels: number[] = []
    for (const reel of reelSet.reels) {
      const count = countSymbolsInReel(reel, rule.targetType, rule.targetId, groups, symbols)
      if (count !== rule.value) {
        failingReels.push(reel.reelIndex)
      }
    }
    const status: ValidationStatus = failingReels.length ? rule.severity : 'pass'
    return baseResult(
      rule,
      status,
      status === 'pass' ? 'Exact count satisfied' : 'Exact count violated',
      `= ${rule.value} per reel`,
      failingReels.length ? `Reels ${failingReels.map((r) => r + 1).join(', ')} differ` : 'OK',
      failingReels,
      [],
      `Adjust each reel to contain exactly ${rule.value}.`,
    )
  }
  const count = countSymbolsGlobal(reelSet.reels, rule.targetType, rule.targetId, groups, symbols)
  const status: ValidationStatus = count === rule.value ? 'pass' : rule.severity
  return baseResult(
    rule,
    status,
    status === 'pass' ? 'Exact count satisfied' : 'Exact count violated',
    `= ${rule.value}`,
    String(count),
    status === 'pass' ? [] : reelSet.reels.map((reel) => reel.reelIndex),
    [],
    `Adjust total count to exactly ${rule.value}.`,
  )
}

function validateReelSpecificCount(
  rule: ConstraintRule,
  input: ConstraintEngineInput,
): ValidationResultItem {
  const { reelSet, symbols, constraintDocument } = input
  const reelIndex = rule.reelIndex ?? 0
  const reel = reelSet.reels.find((item) => item.reelIndex === reelIndex)
  const count = reel
    ? countSymbolsInReel(reel, rule.targetType, rule.targetId, constraintDocument.groups, symbols)
    : 0
  const status: ValidationStatus = count === rule.value ? 'pass' : rule.severity
  const positions: ValidationResultItem['affectedPositions'] = []
  if (reel && status !== 'pass') {
    reel.symbols.forEach((symbolId, symbolIndex) => {
      if (
        symbolMatches(symbolId, rule.targetType, rule.targetId, constraintDocument.groups, symbols)
      ) {
        positions.push({ reelIndex, symbolIndex })
      }
    })
  }
  return baseResult(
    rule,
    status,
    status === 'pass' ? 'Reel count satisfied' : 'Reel-specific count violated',
    `${rule.value} on reel ${reelIndex + 1}`,
    String(count),
    status === 'pass' ? [] : [reelIndex],
    positions,
    `Set reel ${reelIndex + 1} count to ${rule.value}.`,
  )
}

function validateMinConsecutive(
  rule: ConstraintRule,
  input: ConstraintEngineInput,
): ValidationResultItem {
  const { reelSet, symbols, constraintDocument } = input
  const longest = Math.max(
    0,
    ...reelSet.reels.map((reel) =>
      longestStreak(reel, rule.targetType, rule.targetId, constraintDocument.groups, symbols),
    ),
  )
  const status: ValidationStatus = longest >= rule.value ? 'pass' : rule.severity
  return baseResult(
    rule,
    status,
    status === 'pass' ? 'Minimum consecutive satisfied' : 'Minimum consecutive violated',
    `≥ ${rule.value} in a row`,
    String(longest),
    status === 'pass' ? [] : reelSet.reels.map((reel) => reel.reelIndex),
    [],
    `Create a run of at least ${rule.value} consecutive symbols.`,
  )
}

function validateMaxConsecutive(
  rule: ConstraintRule,
  input: ConstraintEngineInput,
): ValidationResultItem {
  const { reelSet, symbols, constraintDocument } = input
  let worst: { length: number; positions: ValidationResultItem['affectedPositions'] } | null = null
  let worstReel = -1
  for (const reel of reelSet.reels) {
    const violation = findStreakViolations(
      reel,
      reel.reelIndex,
      rule.targetType,
      rule.targetId,
      constraintDocument.groups,
      symbols,
      rule.value,
    )
    if (violation && (!worst || violation.length > worst.length)) {
      worst = violation
      worstReel = reel.reelIndex
    }
  }
  const status: ValidationStatus = worst ? rule.severity : 'pass'
  return baseResult(
    rule,
    status,
    status === 'pass' ? 'Maximum consecutive satisfied' : 'Maximum consecutive violated',
    `≤ ${rule.value} in a row`,
    worst ? String(worst.length) : '0',
    worst ? [worstReel] : [],
    worst?.positions ?? [],
    `Break streaks longer than ${rule.value}.`,
  )
}

function findSymbolIndices(
  reel: StudioReelStrip,
  targetType: ConstraintRule['targetType'],
  targetId: string,
  groups: ConstraintEngineInput['constraintDocument']['groups'],
  symbols: ConstraintEngineInput['symbols'],
): number[] {
  const indices: number[] = []
  reel.symbols.forEach((symbolId, index) => {
    if (symbolMatches(symbolId, targetType, targetId, groups, symbols)) {
      indices.push(index)
    }
  })
  return indices
}

function validateMinDistance(rule: ConstraintRule, input: ConstraintEngineInput): ValidationResultItem {
  const { reelSet, symbols, constraintDocument } = input
  const wrap = constraintDocument.edgeWrapping
  const secondaryType = rule.secondaryTargetType ?? rule.targetType
  const secondaryId = rule.secondaryTargetId ?? rule.targetId
  const violations: ValidationResultItem['affectedPositions'] = []
  const failingReels: number[] = []
  let worstDistance = Number.POSITIVE_INFINITY

  for (const reel of reelSet.reels) {
    const primaryIndices = findSymbolIndices(
      reel,
      rule.targetType,
      rule.targetId,
      constraintDocument.groups,
      symbols,
    )
    const secondaryIndices = findSymbolIndices(
      reel,
      secondaryType,
      secondaryId,
      constraintDocument.groups,
      symbols,
    )
    if (primaryIndices.length === 0) {
      continue
    }
    const compareIndices =
      rule.secondaryTargetId || rule.secondaryTargetType
        ? [...primaryIndices, ...secondaryIndices]
        : primaryIndices
    const unique = [...new Set(compareIndices)].sort((a, b) => a - b)
    for (let i = 0; i < unique.length; i += 1) {
      for (let j = i + 1; j < unique.length; j += 1) {
        const a = unique[i]!
        const b = unique[j]!
        const distance = circularDistance(reel.symbols.length, a, b, wrap) - 1
        if (distance < rule.value) {
          worstDistance = Math.min(worstDistance, distance)
          if (!failingReels.includes(reel.reelIndex)) {
            failingReels.push(reel.reelIndex)
          }
          violations.push({ reelIndex: reel.reelIndex, symbolIndex: a })
          violations.push({ reelIndex: reel.reelIndex, symbolIndex: b })
        }
      }
    }
    if (wrap && reel.symbols.length > 1) {
      for (const index of unique) {
        const wrapDistance = circularDistance(reel.symbols.length, index, 0, true) - 1
        if (wrapDistance < rule.value && index !== 0) {
          worstDistance = Math.min(worstDistance, wrapDistance)
          if (!failingReels.includes(reel.reelIndex)) {
            failingReels.push(reel.reelIndex)
          }
          violations.push({ reelIndex: reel.reelIndex, symbolIndex: index })
          violations.push({ reelIndex: reel.reelIndex, symbolIndex: 0 })
        }
      }
    }
  }

  const status: ValidationStatus =
    violations.length === 0 ? 'pass' : rule.severity
  return baseResult(
    rule,
    status,
    status === 'pass' ? 'Minimum distance satisfied' : 'Minimum distance violated',
    `≥ ${rule.value} apart`,
    violations.length ? String(worstDistance) : 'OK',
    failingReels,
    violations,
    `Increase spacing to at least ${rule.value} positions.`,
  )
}

function validateAdjacency(
  rule: ConstraintRule,
  input: ConstraintEngineInput,
  mode: 'forbidden' | 'allowed',
): ValidationResultItem {
  const { reelSet, symbols, constraintDocument } = input
  const wrap = constraintDocument.edgeWrapping
  const secondaryType = rule.secondaryTargetType ?? rule.targetType
  const secondaryId = rule.secondaryTargetId ?? rule.targetId
  const violations: ValidationResultItem['affectedPositions'] = []
  const failingReels: number[] = []

  for (const reel of reelSet.reels) {
    for (let index = 0; index < reel.symbols.length; index += 1) {
      const current = reel.symbols[index]!
      const primary = symbolMatches(
        current,
        rule.targetType,
        rule.targetId,
        constraintDocument.groups,
        symbols,
      )
      if (!primary) {
        continue
      }
      const { prev, next } = getAdjacentIndices(reel.symbols.length, index, wrap)
      for (const neighborIndex of [prev, next]) {
        if (neighborIndex === null) {
          continue
        }
        const neighbor = reel.symbols[neighborIndex]!
        const secondary = symbolMatches(
          neighbor,
          secondaryType,
          secondaryId,
          constraintDocument.groups,
          symbols,
        )
        if (!secondary) {
          continue
        }
        const isForbidden = mode === 'forbidden'
        const violated = isForbidden
        if (violated) {
          if (!failingReels.includes(reel.reelIndex)) {
            failingReels.push(reel.reelIndex)
          }
          violations.push({ reelIndex: reel.reelIndex, symbolIndex: index })
          violations.push({ reelIndex: reel.reelIndex, symbolIndex: neighborIndex })
        }
      }
    }
  }

  if (mode === 'allowed') {
    const allowedTargets = resolveTargetSymbolIds(
      secondaryType,
      secondaryId,
      constraintDocument.groups,
      symbols,
    )
    for (const reel of reelSet.reels) {
      for (let index = 0; index < reel.symbols.length; index += 1) {
        const current = reel.symbols[index]!
        if (
          !symbolMatches(
            current,
            rule.targetType,
            rule.targetId,
            constraintDocument.groups,
            symbols,
          )
        ) {
          continue
        }
        const { prev, next } = getAdjacentIndices(reel.symbols.length, index, wrap)
        for (const neighborIndex of [prev, next]) {
          if (neighborIndex === null) {
            continue
          }
          const neighbor = reel.symbols[neighborIndex]!
          if (!allowedTargets.has(neighbor)) {
            if (!failingReels.includes(reel.reelIndex)) {
              failingReels.push(reel.reelIndex)
            }
            violations.push({ reelIndex: reel.reelIndex, symbolIndex: index })
            violations.push({ reelIndex: reel.reelIndex, symbolIndex: neighborIndex })
          }
        }
      }
    }
  }

  const status: ValidationStatus = violations.length ? rule.severity : 'pass'
  const label = mode === 'forbidden' ? 'Forbidden adjacency' : 'Allowed adjacency'
  return baseResult(
    rule,
    status,
    status === 'pass' ? `${label} satisfied` : `${label} violated`,
    mode === 'forbidden' ? 'No touching pairs' : 'Only whitelisted neighbors',
    violations.length ? `${violations.length / 2} pair(s)` : 'OK',
    failingReels,
    violations,
    mode === 'forbidden'
      ? 'Separate adjacent symbols.'
      : 'Replace neighbors with allowed symbols only.',
  )
}

const VALIDATORS: Record<ConstraintRule['type'], ConstraintValidator> = {
  min_count: validateMinCount,
  max_count: validateMaxCount,
  exact_count: validateExactCount,
  min_consecutive: validateMinConsecutive,
  max_consecutive: validateMaxConsecutive,
  min_distance: validateMinDistance,
  forbidden_adjacency: (rule, input) => validateAdjacency(rule, input, 'forbidden'),
  allowed_adjacency: (rule, input) => validateAdjacency(rule, input, 'allowed'),
  reel_specific_count: validateReelSpecificCount,
}

export function validateConstraint(
  rule: ConstraintRule,
  input: ConstraintEngineInput,
): ValidationResultItem {
  if (!rule.enabled) {
    return baseResult(rule, 'pass', 'Constraint disabled', '—', '—', [], [])
  }
  const validator = VALIDATORS[rule.type]
  return validator(rule, input)
}

export function runConstraintEngine(input: ConstraintEngineInput): ConstraintValidationReport {
  const results = input.constraintDocument.constraints.map((rule) =>
    validateConstraint(rule, input),
  )
  const inventoryResults = validateInventory(input)
  const allResults = [...results, ...inventoryResults]

  const summary = { pass: 0, warning: 0, error: 0, byCategory: {} as Record<string, ValidationStatus> }
  const violationsByPosition: Record<string, ValidationResultItem[]> = {}

  for (const result of allResults) {
    summary[result.status] += 1
    const current = summary.byCategory[result.category]
    if (!current || (result.status === 'error' && current !== 'error')) {
      summary.byCategory[result.category] = result.status
    } else if (result.status === 'warning' && current === 'pass') {
      summary.byCategory[result.category] = 'warning'
    }
    if (result.status !== 'pass') {
      for (const position of result.affectedPositions) {
        const key = positionKey(position.reelIndex, position.symbolIndex)
        violationsByPosition[key] = [...(violationsByPosition[key] ?? []), result]
      }
    }
  }

  return { results: allResults, summary, violationsByPosition }
}

function validateInventory(input: ConstraintEngineInput): ValidationResultItem[] {
  const { reelSet, constraintDocument } = input
  const results: ValidationResultItem[] = []
  for (const entry of Object.values(constraintDocument.inventory)) {
    let actualTotal = 0
    const reelActuals: string[] = []
    for (const reel of reelSet.reels) {
      const count = reel.symbols.filter((id) => id === entry.symbolId).length
      actualTotal += count
      const target = entry.reelCounts[String(reel.reelIndex)] ?? 0
      if (target > 0 && count !== target) {
        reelActuals.push(`R${reel.reelIndex + 1}:${count}/${target}`)
      }
    }
    const totalMismatch =
      entry.totalTarget > 0 && actualTotal !== entry.totalTarget
    if (reelActuals.length === 0 && !totalMismatch) {
      continue
    }
    const pseudoRule: ConstraintRule = {
      id: `inventory-${entry.symbolId}`,
      type: 'exact_count',
      enabled: true,
      description: `Inventory target for ${entry.symbolId}`,
      targetType: 'symbol',
      targetId: entry.symbolId,
      value: entry.totalTarget,
      scope: 'global',
      severity: 'warning',
    }
    results.push(
      baseResult(
        pseudoRule,
        'warning',
        'Inventory target mismatch',
        entry.totalTarget > 0 ? `Total ${entry.totalTarget}` : reelActuals.join(', '),
        totalMismatch ? String(actualTotal) : reelActuals.join(', '),
        reelSet.reels.map((reel) => reel.reelIndex),
        [],
        'Align reel strips with inventory targets.',
      ),
    )
  }
  return results
}
