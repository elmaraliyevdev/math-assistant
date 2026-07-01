import type { SymbolGroup } from '@/features/reel-studio/constraints/types'
import type { StudioReelSet, StudioSymbol } from '@/features/reel-studio/types'

export interface AdvancedReelStatistics {
  symbolFrequencies: Record<string, number>
  reelFrequencies: Record<number, Record<string, number>>
  entropy: number
  duplicatePercent: number
  longestStreaks: Record<string, number>
  distanceHistogram: Record<string, Record<number, number>>
  groupFrequencies: Record<string, number>
}

function shannonEntropy(counts: number[]): number {
  const total = counts.reduce((sum, value) => sum + value, 0)
  if (total === 0) {
    return 0
  }
  let entropy = 0
  for (const count of counts) {
    if (count <= 0) {
      continue
    }
    const p = count / total
    entropy -= p * Math.log2(p)
  }
  return entropy
}

function longestRun(symbols: string[], targetIds: Set<string>): number {
  let longest = 0
  let current = 0
  for (const symbolId of symbols) {
    if (targetIds.has(symbolId)) {
      current += 1
      longest = Math.max(longest, current)
    } else {
      current = 0
    }
  }
  return longest
}

function distanceHistogramForSymbol(
  symbols: string[],
  symbolId: string,
  wrap: boolean,
): Record<number, number> {
  const histogram: Record<number, number> = {}
  const indices = symbols
    .map((id, index) => (id === symbolId ? index : -1))
    .filter((index) => index >= 0)
  for (let i = 0; i < indices.length; i += 1) {
    for (let j = i + 1; j < indices.length; j += 1) {
      const a = indices[i]!
      const b = indices[j]!
      const linear = Math.abs(b - a)
      const forward = (b - a + symbols.length) % symbols.length
      const backward = (a - b + symbols.length) % symbols.length
      const distance = wrap ? Math.min(linear, forward, backward) - 1 : linear - 1
      const key = Math.max(0, distance)
      histogram[key] = (histogram[key] ?? 0) + 1
    }
  }
  return histogram
}

export function computeAdvancedStatistics(
  reelSet: StudioReelSet,
  symbols: Record<string, StudioSymbol>,
  groups: SymbolGroup[],
  edgeWrapping: boolean,
): AdvancedReelStatistics {
  const symbolFrequencies: Record<string, number> = {}
  const reelFrequencies: Record<number, Record<string, number>> = {}
  const longestStreaks: Record<string, number> = {}
  const distanceHistogram: Record<string, Record<number, number>> = {}
  const groupFrequencies: Record<string, number> = {}
  let duplicateCount = 0
  let totalSymbols = 0

  for (const reel of reelSet.reels) {
    reelFrequencies[reel.reelIndex] = {}
    const counts = new Map<string, number>()
    for (const symbolId of reel.symbols) {
      totalSymbols += 1
      symbolFrequencies[symbolId] = (symbolFrequencies[symbolId] ?? 0) + 1
      reelFrequencies[reel.reelIndex]![symbolId] =
        (reelFrequencies[reel.reelIndex]![symbolId] ?? 0) + 1
      counts.set(symbolId, (counts.get(symbolId) ?? 0) + 1)
    }
    for (const count of counts.values()) {
      if (count > 1) {
        duplicateCount += count
      }
    }
    for (const symbolId of Object.keys(symbols)) {
      longestStreaks[symbolId] = Math.max(
        longestStreaks[symbolId] ?? 0,
        longestRun(reel.symbols, new Set([symbolId])),
      )
      distanceHistogram[symbolId] = {
        ...(distanceHistogram[symbolId] ?? {}),
        ...Object.fromEntries(
          Object.entries(distanceHistogramForSymbol(reel.symbols, symbolId, edgeWrapping)).map(
            ([distance, value]) => [
              distance,
              (distanceHistogram[symbolId]?.[Number(distance)] ?? 0) + value,
            ],
          ),
        ),
      }
    }
  }

  for (const group of groups) {
    const target = new Set(group.symbolIds)
    groupFrequencies[group.id] = Object.entries(symbolFrequencies).reduce(
      (sum, [symbolId, count]) => (target.has(symbolId) ? sum + count : sum),
      0,
    )
  }

  return {
    symbolFrequencies,
    reelFrequencies,
    entropy: shannonEntropy(Object.values(symbolFrequencies)),
    duplicatePercent: totalSymbols > 0 ? (duplicateCount / totalSymbols) * 100 : 0,
    longestStreaks,
    distanceHistogram,
    groupFrequencies,
  }
}
