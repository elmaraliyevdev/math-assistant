import type { ReelSetStats, ReelStats, ReelSymbolStats, StudioReelSet } from '@/features/reel-studio/types'

function buildSymbolStats(symbols: string[]): {
  distribution: ReelSymbolStats[]
  duplicateSymbolIds: string[]
} {
  if (symbols.length === 0) {
    return { distribution: [], duplicateSymbolIds: [] }
  }
  const counts = new Map<string, number>()
  for (const symbolId of symbols) {
    counts.set(symbolId, (counts.get(symbolId) ?? 0) + 1)
  }
  const distribution = [...counts.entries()]
    .map(([symbolId, count]) => ({
      symbolId,
      count,
      percentage: (count / symbols.length) * 100,
    }))
    .sort((a, b) => b.count - a.count || a.symbolId.localeCompare(b.symbolId))

  const duplicateSymbolIds = distribution
    .filter((item) => item.count > 1)
    .map((item) => item.symbolId)

  return { distribution, duplicateSymbolIds }
}

function buildReelStats(reelIndex: number, symbols: string[]): ReelStats {
  const { distribution, duplicateSymbolIds } = buildSymbolStats(symbols)
  return {
    reelIndex,
    length: symbols.length,
    symbols: distribution,
    duplicateSymbolIds,
  }
}

export function computeReelSetStats(reelSet: StudioReelSet): ReelSetStats {
  const reels = reelSet.reels.map((reel) =>
    buildReelStats(reel.reelIndex, reel.symbols),
  )
  const allSymbols = reelSet.reels.flatMap((reel) => reel.symbols)
  const totals = buildSymbolStats(allSymbols)

  return {
    reelSetId: reelSet.id,
    reels,
    totals: {
      totalSymbols: allSymbols.length,
      symbolCounts: totals.distribution,
      duplicateSymbolIds: totals.duplicateSymbolIds,
    },
  }
}
