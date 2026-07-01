import { computeAdvancedStatistics } from '@/features/reel-studio/constraints/lib/advanced-statistics'
import { computeDistribution } from '@/features/reel-studio/generator/distribution'
import type { DesignGoals } from '@/features/reel-studio/generator/types'
import type { GoalEvaluation } from '@/features/reel-studio/optimizer/optimizer-types'
import type { StudioReelSet, StudioSymbol } from '@/features/reel-studio/types'

function statusFromGap(gap: number, warnThreshold: number, errorThreshold: number): GoalEvaluation['status'] {
  if (gap <= warnThreshold) {
    return 'pass'
  }
  if (gap <= errorThreshold) {
    return 'warning'
  }
  return 'error'
}

export function evaluateDesignGoals(
  reelSet: StudioReelSet,
  symbols: Record<string, StudioSymbol>,
  designGoals: DesignGoals,
  edgeWrapping: boolean,
  groups: { id: string; name: string; symbolIds: string[] }[],
): GoalEvaluation[] {
  const reels = reelSet.reels.map((reel) => reel.symbols)
  const flat = reels.flat()
  const total = flat.length || 1
  const distribution = computeDistribution(reels)
  const stats = computeAdvancedStatistics(reelSet, symbols, groups, edgeWrapping)

  const wildCount = flat.filter((id) => symbols[id]?.type === 'wild').length
  const scatterCount = flat.filter((id) => symbols[id]?.type === 'scatter').length
  const bonusCount = flat.filter((id) => symbols[id]?.type === 'bonus').length

  const wildTarget = Math.max(1, Math.floor(total / designGoals.wildEveryNSymbols))
  const scatterTarget = Math.max(1, Math.floor(total / designGoals.scatterEveryNSymbols))
  const featureTarget =
    designGoals.featureFrequency === 'high' ? 12 : designGoals.featureFrequency === 'low' ? 4 : 8

  const volatilityGap =
    designGoals.volatility === 'low'
      ? Math.max(0, stats.duplicatePercent - 15)
      : designGoals.volatility === 'high'
        ? Math.max(0, 25 - stats.duplicatePercent)
        : Math.abs(stats.duplicatePercent - 20)

  const symbolBalanceValues = Object.values(distribution).map((perReel) => {
    const counts = Object.values(perReel)
    if (counts.length === 0) {
      return 0
    }
    const mean = counts.reduce((sum, value) => sum + value, 0) / counts.length
    return counts.reduce((sum, value) => sum + Math.abs(value - mean), 0) / counts.length
  })
  const balanceGap = symbolBalanceValues.reduce((sum, value) => sum + value, 0)

  return [
    {
      goalId: 'volatility',
      label: 'Target volatility',
      target: designGoals.volatility,
      current: `duplicate ${stats.duplicatePercent.toFixed(1)}%`,
      status: statusFromGap(volatilityGap, 5, 12),
      gap: volatilityGap,
    },
    {
      goalId: 'hit-rate',
      label: 'Target hit rate',
      target: `${designGoals.hitRatePercent}%`,
      current: 'design metadata only',
      status: 'pass',
      gap: 0,
    },
    {
      goalId: 'feature-frequency',
      label: 'Target feature frequency',
      target: designGoals.featureFrequency,
      current: `${bonusCount} bonus symbols`,
      status: statusFromGap(Math.abs(bonusCount - featureTarget), 2, 5),
      gap: Math.abs(bonusCount - featureTarget),
    },
    {
      goalId: 'wild-frequency',
      label: 'Wild frequency',
      target: `~every ${designGoals.wildEveryNSymbols}`,
      current: `${wildCount} wilds`,
      status: statusFromGap(Math.abs(wildCount - wildTarget), 2, 4),
      gap: Math.abs(wildCount - wildTarget),
    },
    {
      goalId: 'scatter-frequency',
      label: 'Scatter frequency',
      target: `~every ${designGoals.scatterEveryNSymbols}`,
      current: `${scatterCount} scatters`,
      status: statusFromGap(Math.abs(scatterCount - scatterTarget), 2, 4),
      gap: Math.abs(scatterCount - scatterTarget),
    },
    {
      goalId: 'symbol-balance',
      label: 'Symbol balance',
      target: 'even per-reel distribution',
      current: `avg deviation ${balanceGap.toFixed(1)}`,
      status: statusFromGap(balanceGap, 1.5, 3),
      gap: balanceGap,
    },
    {
      goalId: 'entropy',
      label: 'Target entropy',
      target: '>= 2.5',
      current: stats.entropy.toFixed(2),
      status: statusFromGap(Math.max(0, 2.5 - stats.entropy), 0.3, 0.8),
      gap: Math.max(0, 2.5 - stats.entropy),
    },
    {
      goalId: 'spacing',
      label: 'Feature spacing',
      target: 'low clustering',
      current: `entropy ${stats.entropy.toFixed(2)}`,
      status: stats.entropy >= 2.2 ? 'pass' : 'warning',
      gap: Math.max(0, 2.2 - stats.entropy),
    },
  ]
}
