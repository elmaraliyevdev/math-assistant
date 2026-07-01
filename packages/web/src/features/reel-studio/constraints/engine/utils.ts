import type { ConstraintDocument, ConstraintTargetType, SymbolGroup } from '@/features/reel-studio/constraints/types'
import type { StudioReelStrip, StudioSymbol } from '@/features/reel-studio/types'

export function resolveTargetSymbolIds(
  targetType: ConstraintTargetType,
  targetId: string,
  groups: SymbolGroup[],
  symbols: Record<string, StudioSymbol>,
): Set<string> {
  if (targetType === 'symbol') {
    return symbols[targetId] ? new Set([targetId]) : new Set()
  }
  const group = groups.find((item) => item.id === targetId)
  return new Set(group?.symbolIds ?? [])
}

export function symbolMatches(
  symbolId: string,
  targetType: ConstraintTargetType,
  targetId: string,
  groups: SymbolGroup[],
  symbols: Record<string, StudioSymbol>,
): boolean {
  return resolveTargetSymbolIds(targetType, targetId, groups, symbols).has(symbolId)
}

export function countSymbolsInReel(
  reel: StudioReelStrip,
  targetType: ConstraintTargetType,
  targetId: string,
  groups: SymbolGroup[],
  symbols: Record<string, StudioSymbol>,
): number {
  const targets = resolveTargetSymbolIds(targetType, targetId, groups, symbols)
  return reel.symbols.filter((id) => targets.has(id)).length
}

export function countSymbolsGlobal(
  reels: StudioReelStrip[],
  targetType: ConstraintTargetType,
  targetId: string,
  groups: SymbolGroup[],
  symbols: Record<string, StudioSymbol>,
): number {
  return reels.reduce(
    (total, reel) => total + countSymbolsInReel(reel, targetType, targetId, groups, symbols),
    0,
  )
}

export function circularDistance(length: number, from: number, to: number, wrap: boolean): number {
  if (length <= 1) {
    return 0
  }
  const forward = (to - from + length) % length
  const backward = (from - to + length) % length
  const linear = Math.abs(to - from)
  if (!wrap) {
    return linear
  }
  return Math.min(linear, forward, backward)
}

export function getAdjacentIndices(
  length: number,
  index: number,
  wrap: boolean,
): { prev: number | null; next: number | null } {
  if (length === 0) {
    return { prev: null, next: null }
  }
  if (length === 1) {
    return wrap ? { prev: 0, next: 0 } : { prev: null, next: null }
  }
  const prev = index === 0 ? (wrap ? length - 1 : null) : index - 1
  const next = index === length - 1 ? (wrap ? 0 : null) : index + 1
  return { prev, next }
}

export function longestStreak(
  reel: StudioReelStrip,
  targetType: ConstraintTargetType,
  targetId: string,
  groups: SymbolGroup[],
  symbols: Record<string, StudioSymbol>,
): number {
  let longest = 0
  let current = 0
  for (const symbolId of reel.symbols) {
    if (symbolMatches(symbolId, targetType, targetId, groups, symbols)) {
      current += 1
      longest = Math.max(longest, current)
    } else {
      current = 0
    }
  }
  return longest
}

export function findStreakViolations(
  reel: StudioReelStrip,
  reelIndex: number,
  targetType: ConstraintTargetType,
  targetId: string,
  groups: SymbolGroup[],
  symbols: Record<string, StudioSymbol>,
  maxAllowed: number,
): { length: number; positions: Array<{ reelIndex: number; symbolIndex: number }> } | null {
  let current = 0
  let start = 0
  let worst: { length: number; positions: Array<{ reelIndex: number; symbolIndex: number }> } | null =
    null
  for (let index = 0; index <= reel.symbols.length; index += 1) {
    const symbolId = reel.symbols[index]
    const matches =
      symbolId !== undefined &&
      symbolMatches(symbolId, targetType, targetId, groups, symbols)
    if (matches) {
      if (current === 0) {
        start = index
      }
      current += 1
    } else if (current > maxAllowed) {
      const positions = Array.from({ length: current }, (_, offset) => ({
        reelIndex,
        symbolIndex: start + offset,
      }))
      if (!worst || current > worst.length) {
        worst = { length: current, positions }
      }
      current = 0
    } else {
      current = 0
    }
  }
  return worst
}

export function createDefaultConstraintDocument(
  symbolIds: string[],
  reelCount: number,
): ConstraintDocument {
  const inventory: ConstraintDocument['inventory'] = {}
  for (const symbolId of symbolIds) {
    const reelCounts: Record<string, number> = {}
    for (let reelIndex = 0; reelIndex < reelCount; reelIndex += 1) {
      reelCounts[String(reelIndex)] = 0
    }
    inventory[symbolId] = { symbolId, reelCounts, totalTarget: 0 }
  }
  return {
    version: 1,
    edgeWrapping: true,
    groups: [],
    inventory,
    constraints: [],
  }
}
