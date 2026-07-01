import { runConstraintEngine } from '@/features/reel-studio/constraints/engine'
import type { ConstraintDocument } from '@/features/reel-studio/constraints/types'
import { computeDistribution } from '@/features/reel-studio/generator/distribution'
import { computeDesignHealth } from '@/features/reel-studio/generator/health'
import type { OptimizationIteration } from '@/features/reel-studio/optimizer/optimizer-types'
import type { StudioReelStrip, StudioSymbol } from '@/features/reel-studio/types'

export function createIterationSnapshot(
  reels: StudioReelStrip[],
  symbols: Record<string, StudioSymbol>,
  constraintDocument: ConstraintDocument,
  options: {
    id: string
    parentId: string | null
    branchLabel: string
    timestamp: number
    seed: number
    proposalId: string | null
    proposalTitle: string | null
    previousHealth: number
    healthReasons: string[]
  },
): OptimizationIteration {
  const reelSet = { id: 'iteration', reels }
  const health = computeDesignHealth(reelSet, symbols, constraintDocument).overallScore
  const validation = runConstraintEngine({ reelSet, symbols, constraintDocument })
  const distribution = computeDistribution(reels.map((reel) => reel.symbols))

  return {
    id: options.id,
    parentId: options.parentId,
    branchLabel: options.branchLabel,
    timestamp: options.timestamp,
    seed: options.seed,
    health,
    healthDelta: health - options.previousHealth,
    proposalId: options.proposalId,
    proposalTitle: options.proposalTitle,
    reels: reels.map((reel) => ({ ...reel, symbols: [...reel.symbols] })),
    distribution,
    constraintSummary: {
      pass: validation.summary.pass,
      warning: validation.summary.warning,
      error: validation.summary.error,
    },
    healthReasons: options.healthReasons,
  }
}

export function healthEvolutionPath(iterations: OptimizationIteration[]): number[] {
  return iterations.map((iteration) => iteration.health)
}

export function explainHealthDelta(iteration: OptimizationIteration): string[] {
  const reasons = [...iteration.healthReasons]
  if (iteration.proposalTitle) {
    reasons.unshift(`Applied: ${iteration.proposalTitle}`)
  }
  if (iteration.healthDelta > 0) {
    reasons.push(`Health improved by ${iteration.healthDelta}`)
  } else if (iteration.healthDelta < 0) {
    reasons.push(`Health decreased by ${Math.abs(iteration.healthDelta)}`)
  }
  return reasons
}
