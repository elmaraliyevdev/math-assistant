import { runConstraintEngine } from '@/features/reel-studio/constraints/engine'
import type { ConstraintDocument } from '@/features/reel-studio/constraints/types'
import { computeDistribution } from '@/features/reel-studio/generator/distribution'
import { scoreCandidate } from '@/features/reel-studio/generator/scoring'
import type {
  DesignHealthMetric,
  DesignHealthReport,
  SmartSuggestion,
} from '@/features/reel-studio/generator/types'
import type { StudioReelSet, StudioSymbol } from '@/features/reel-studio/types'

function clamp(value: number): number {
  return Math.max(0, Math.min(100, value))
}

export function computeDesignHealth(
  reelSet: StudioReelSet,
  symbols: Record<string, StudioSymbol>,
  constraintDocument: ConstraintDocument,
): DesignHealthReport {
  const reels = reelSet.reels.map((reel) => reel.symbols)
  const validation = runConstraintEngine({ reelSet, symbols, constraintDocument })
  const breakdown = scoreCandidate(reels, symbols, constraintDocument, 0)
  const distribution = computeDistribution(reels)

  const metrics: DesignHealthMetric[] = [
    {
      id: 'constraints',
      label: 'Constraint satisfaction',
      score: breakdown.constraintSatisfaction,
      status: validation.summary.error > 0 ? 'error' : validation.summary.warning > 0 ? 'warning' : 'pass',
      detail: `${validation.summary.error} errors, ${validation.summary.warning} warnings`,
    },
    {
      id: 'symbol-balance',
      label: 'Symbol balance',
      score: breakdown.symbolBalance,
      status: breakdown.symbolBalance >= 85 ? 'pass' : breakdown.symbolBalance >= 70 ? 'warning' : 'error',
      detail: 'Inventory alignment across reels',
    },
    {
      id: 'reel-balance',
      label: 'Reel balance',
      score: breakdown.reelBalance,
      status: breakdown.reelBalance >= 85 ? 'pass' : 'warning',
      detail: 'Per-reel distribution evenness',
    },
    {
      id: 'feature-spacing',
      label: 'Feature spacing',
      score: breakdown.spacing,
      status: breakdown.spacing >= 80 ? 'pass' : 'warning',
      detail: 'Wild and scatter spacing quality',
    },
    {
      id: 'inventory',
      label: 'Inventory',
      score: breakdown.inventory,
      status: breakdown.inventory >= 85 ? 'pass' : 'warning',
      detail: 'Target vs actual symbol counts',
    },
    {
      id: 'entropy',
      label: 'Entropy',
      score: clamp(breakdown.distributionQuality),
      status: breakdown.distributionQuality >= 75 ? 'pass' : 'warning',
      detail: 'Symbol diversity across layout',
    },
    {
      id: 'scatter-clustering',
      label: 'Scatter clustering',
      score: breakdown.clustering,
      status: breakdown.clustering >= 80 ? 'pass' : 'warning',
      detail: 'Scatter adjacency and runs',
    },
    {
      id: 'wild-clustering',
      label: 'Wild clustering',
      score: breakdown.clustering,
      status: breakdown.clustering >= 80 ? 'pass' : 'warning',
      detail: 'Wild adjacency and runs',
    },
  ]

  const recommendations: string[] = []
  for (const entry of Object.values(constraintDocument.inventory)) {
    if (entry.totalTarget <= 0) {
      continue
    }
    const actual = reels.flat().filter((id) => id === entry.symbolId).length
    const diff = entry.totalTarget - actual
    if (diff > 0) {
      const reelTotals = reelSet.reels.map(
        (reel) => reel.symbols.filter((id) => id === entry.symbolId).length,
      )
      const donorReel = reelTotals.findIndex((count) => count > 0)
      const receiverReel = reelTotals.findIndex((count) => count === Math.min(...reelTotals))
      if (donorReel >= 0 && receiverReel >= 0 && donorReel !== receiverReel) {
        recommendations.push(
          `Move one ${entry.symbolId} from Reel ${donorReel + 1} to Reel ${receiverReel + 1}.`,
        )
      } else {
        recommendations.push(`Add ${diff} more ${entry.symbolId} symbol(s) to reach inventory target.`)
      }
    }
  }

  for (const result of validation.results) {
    if (result.status === 'pass' || !result.suggestedFix) {
      continue
    }
    if (result.constraintType === 'max_consecutive' || result.constraintType === 'forbidden_adjacency') {
      const reel = result.affectedReels[0]
      if (reel !== undefined) {
        recommendations.push(`Reduce ${result.description.toLowerCase()} on Reel ${reel + 1}.`)
      }
    }
    if (result.constraintType === 'min_distance' && result.affectedPositions[0]) {
      const pos = result.affectedPositions[0]
      recommendations.push(
        `Increase spacing for ${result.description} on Reel ${pos.reelIndex + 1} position ${pos.symbolIndex + 1}.`,
      )
    }
  }

  const symbolIds = Object.keys(distribution)
  for (const symbolId of symbolIds) {
    const counts = distribution[symbolId] ?? {}
    const values = Object.values(counts)
    if (values.length < 2) {
      continue
    }
    const max = Math.max(...values)
    const min = Math.min(...values)
    if (max - min >= 3) {
      const heavyReel = Number(
        Object.entries(counts).find(([, count]) => count === max)?.[0] ?? 0,
      )
      recommendations.push(`Rebalance ${symbolId}: reduce concentration on Reel ${heavyReel + 1}.`)
    }
  }

  const overallScore = clamp(
    metrics.reduce((sum, metric) => sum + metric.score, 0) / metrics.length,
  )

  return {
    overallScore: Math.round(overallScore),
    metrics,
    recommendations: recommendations.slice(0, 5),
  }
}

export function buildSmartSuggestions(
  reelSet: StudioReelSet,
  symbols: Record<string, StudioSymbol>,
  constraintDocument: ConstraintDocument,
): SmartSuggestion[] {
  const validation = runConstraintEngine({ reelSet, symbols, constraintDocument })
  const suggestions: SmartSuggestion[] = []

  for (const result of validation.results) {
    if (result.status === 'pass' || result.affectedPositions.length === 0) {
      continue
    }
    const from = result.affectedPositions[0]!
    const toReel = result.affectedReels.find((reel) => reel !== from.reelIndex) ?? from.reelIndex
    const toPosition = Math.max(0, from.symbolIndex + 3)
    const symbolId =
      result.constraintType === 'forbidden_adjacency' || result.constraintType === 'min_distance'
        ? reelSet.reels[from.reelIndex]?.symbols[from.symbolIndex] ?? result.description
        : result.description

    suggestions.push({
      id: `suggestion-${result.constraintId}-${from.reelIndex}-${from.symbolIndex}`,
      action: result.suggestedFix ?? 'Relocate symbol to improve constraint satisfaction',
      fromReel: from.reelIndex,
      fromPosition: from.symbolIndex,
      toReel,
      toPosition,
      symbolId,
      expectedImprovements: [
        'remove violation',
        'improve spacing',
        'increase balance',
      ].slice(0, result.status === 'error' ? 3 : 2),
    })
    if (suggestions.length >= 8) {
      break
    }
  }

  return suggestions
}
