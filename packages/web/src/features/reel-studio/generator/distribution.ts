import type { ConstraintDocument } from '@/features/reel-studio/constraints/types'
import type { DesignGoals } from '@/features/reel-studio/generator/types'
import type { StudioSymbol } from '@/features/reel-studio/types'

export function buildSymbolPool(
  symbols: Record<string, StudioSymbol>,
  constraintDocument: ConstraintDocument,
  designGoals: DesignGoals,
  totalLength: number,
): string[] {
  const pool: string[] = []
  const symbolIds = Object.keys(symbols)

  for (const symbolId of symbolIds) {
    const inventory = constraintDocument.inventory[symbolId]
    let count = inventory?.totalTarget ?? 0
    if (count <= 0) {
      const symbol = symbols[symbolId]
      if (symbol?.type === 'wild') {
        count = Math.max(1, Math.floor(totalLength / designGoals.wildEveryNSymbols))
      } else if (symbol?.type === 'scatter') {
        count = Math.max(1, Math.floor(totalLength / designGoals.scatterEveryNSymbols))
      } else if (symbol?.type === 'bonus') {
        count = designGoals.featureFrequency === 'high' ? 12 : designGoals.featureFrequency === 'low' ? 4 : 8
      } else if (symbolId.startsWith('H') || symbolId.includes('HIGH')) {
        count = Math.floor(totalLength * 0.08)
      } else {
        count = Math.floor(totalLength * 0.12)
      }
    }
    for (let index = 0; index < count; index += 1) {
      pool.push(symbolId)
    }
  }

  const targetTotal = totalLength
  if (pool.length < targetTotal) {
    const filler = symbolIds.find((id) => symbols[id]?.type === 'regular') ?? symbolIds[0]
    if (filler) {
      while (pool.length < targetTotal) {
        pool.push(filler)
      }
    }
  } else if (pool.length > targetTotal) {
    pool.length = targetTotal
  }

  return pool
}

export function distributeCountsAcrossReels(
  totalCount: number,
  reelCount: number,
): number[] {
  const base = Math.floor(totalCount / reelCount)
  const remainder = totalCount % reelCount
  return Array.from({ length: reelCount }, (_, index) => base + (index < remainder ? 1 : 0))
}

export function buildPerReelDistribution(
  pool: string[],
  reelCount: number,
  reelLengths: number[],
): string[][] {
  const reels: string[][] = reelLengths.map(() => [])
  let poolIndex = 0
  for (let reelIndex = 0; reelIndex < reelCount; reelIndex += 1) {
    const length = reelLengths[reelIndex] ?? 0
    for (let position = 0; position < length; position += 1) {
      reels[reelIndex]!.push(pool[poolIndex % pool.length] ?? 'A')
      poolIndex += 1
    }
  }
  return reels
}

export function computeDistribution(
  reels: string[][],
): Record<string, Record<number, number>> {
  const distribution: Record<string, Record<number, number>> = {}
  reels.forEach((reel, reelIndex) => {
    for (const symbolId of reel) {
      distribution[symbolId] ??= {}
      distribution[symbolId]![reelIndex] = (distribution[symbolId]![reelIndex] ?? 0) + 1
    }
  })
  return distribution
}
