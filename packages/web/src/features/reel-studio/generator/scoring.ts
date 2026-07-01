import { runConstraintEngine } from '@/features/reel-studio/constraints/engine'
import type { ConstraintDocument } from '@/features/reel-studio/constraints/types'
import { computeAdvancedStatistics } from '@/features/reel-studio/constraints/lib/advanced-statistics'
import { computeDistribution } from '@/features/reel-studio/generator/distribution'
import type { CandidateStatistics } from '@/features/reel-studio/generator/types'
import type { StudioReelSet, StudioSymbol } from '@/features/reel-studio/types'

export interface ScoreBreakdown {
  constraintSatisfaction: number
  symbolBalance: number
  reelBalance: number
  distributionQuality: number
  clustering: number
  spacing: number
  inventory: number
  repairPenalty: number
  total: number
}

function clamp(value: number, min = 0, max = 100): number {
  return Math.max(min, Math.min(max, value))
}

function reelBalanceScore(distribution: Record<string, Record<number, number>>, reelCount: number): number {
  const symbolIds = Object.keys(distribution)
  if (symbolIds.length === 0 || reelCount === 0) {
    return 100
  }
  let totalDeviation = 0
  let comparisons = 0
  for (const symbolId of symbolIds) {
    const counts = distribution[symbolId] ?? {}
    const values = Array.from({ length: reelCount }, (_, index) => counts[index] ?? 0)
    const mean = values.reduce((sum, value) => sum + value, 0) / reelCount
    if (mean === 0) {
      continue
    }
    for (const value of values) {
      totalDeviation += Math.abs(value - mean) / mean
      comparisons += 1
    }
  }
  if (comparisons === 0) {
    return 100
  }
  const avgDeviation = totalDeviation / comparisons
  return clamp(100 - avgDeviation * 40)
}

function clusteringScore(
  reels: string[][],
  symbols: Record<string, StudioSymbol>,
): number {
  const featureIds = Object.entries(symbols)
    .filter(([, symbol]) => symbol.type === 'wild' || symbol.type === 'scatter' || symbol.type === 'bonus')
    .map(([id]) => id)
  if (featureIds.length === 0) {
    return 100
  }
  let penalty = 0
  for (const reel of reels) {
    for (const symbolId of featureIds) {
      let streak = 0
      for (const current of reel) {
        if (current === symbolId) {
          streak += 1
          if (streak > 1) {
            penalty += 5
          }
        } else {
          streak = 0
        }
      }
    }
  }
  return clamp(100 - penalty)
}

function inventoryScore(
  reels: string[][],
  constraintDocument: ConstraintDocument,
): number {
  const entries = Object.values(constraintDocument.inventory)
  if (entries.length === 0) {
    return 100
  }
  let mismatches = 0
  for (const entry of entries) {
    if (entry.totalTarget <= 0) {
      continue
    }
    const actual = reels.flat().filter((id) => id === entry.symbolId).length
    mismatches += Math.abs(actual - entry.totalTarget) / entry.totalTarget
  }
  return clamp(100 - mismatches * 30)
}

export function computeCandidateStatistics(
  reels: string[][],
  symbols: Record<string, StudioSymbol>,
  groups: ConstraintDocument['groups'],
  edgeWrapping: boolean,
): CandidateStatistics {
  const reelSet: StudioReelSet = {
    id: 'candidate',
    reels: reels.map((strip, reelIndex) => ({ reelIndex, symbols: strip })),
  }
  const advanced = computeAdvancedStatistics(reelSet, symbols, groups, edgeWrapping)
  const symbolCounts: Record<string, number> = {}
  for (const reel of reels) {
    for (const symbolId of reel) {
      symbolCounts[symbolId] = (symbolCounts[symbolId] ?? 0) + 1
    }
  }
  return {
    entropy: advanced.entropy,
    duplicatePercent: advanced.duplicatePercent,
    symbolCounts,
    reelLengths: reels.map((reel) => reel.length),
  }
}

export function scoreCandidate(
  reels: string[][],
  symbols: Record<string, StudioSymbol>,
  constraintDocument: ConstraintDocument,
  repairCount: number,
): ScoreBreakdown {
  const reelSet: StudioReelSet = {
    id: 'candidate',
    reels: reels.map((strip, reelIndex) => ({ reelIndex, symbols: strip })),
  }
  const validation = runConstraintEngine({ reelSet, symbols, constraintDocument })
  const distribution = computeDistribution(reels)
  const reelCount = reels.length

  const errorCount = validation.summary.error
  const warningCount = validation.summary.warning
  const constraintSatisfaction = clamp(100 - errorCount * 12 - warningCount * 4)

  const symbolBalance = inventoryScore(reels, constraintDocument)
  const reelBalance = reelBalanceScore(distribution, reelCount)
  const distributionQuality = reelBalance
  const clustering = clusteringScore(reels, symbols)
  const spacing = clustering
  const inventory = symbolBalance
  const repairPenalty = clamp(repairCount * 2)

  const total = clamp(
    constraintSatisfaction * 0.35 +
      symbolBalance * 0.15 +
      reelBalance * 0.15 +
      distributionQuality * 0.1 +
      clustering * 0.1 +
      spacing * 0.05 +
      inventory * 0.1 -
      repairPenalty,
  )

  return {
    constraintSatisfaction,
    symbolBalance,
    reelBalance,
    distributionQuality,
    clustering,
    spacing,
    inventory,
    repairPenalty,
    total,
  }
}
