import { runConstraintEngine } from '@/features/reel-studio/constraints/engine'
import { computeDesignHealth } from '@/features/reel-studio/generator/health'
import { evaluateDesignGoals } from '@/features/reel-studio/optimizer/goal-evaluator'
import type { OptimizationStrategy } from '@/features/reel-studio/optimizer/interfaces'
import type { OptimizerInput, OptimizerOutput } from '@/features/reel-studio/optimizer/optimizer-types'
import { generateProposals } from '@/features/reel-studio/optimizer/proposal'
import { rankProposals } from '@/features/reel-studio/optimizer/proposal-ranking'

export class DeterministicOptimizationEngine implements OptimizationStrategy {
  generateProposals(input: OptimizerInput): OptimizerOutput {
    const reelSet = { id: 'optimizer', reels: input.reels }
    const currentHealth = computeDesignHealth(
      reelSet,
      input.symbols,
      input.constraintDocument,
    ).overallScore
    const proposals = rankProposals(generateProposals(input))
    const goalEvaluation = evaluateDesignGoals(
      reelSet,
      input.symbols,
      input.designGoals,
      input.constraintDocument.edgeWrapping,
      input.constraintDocument.groups,
    )

    return {
      proposals,
      goalEvaluation,
      currentHealth,
    }
  }
}

export function runOptimizationEngine(input: OptimizerInput): OptimizerOutput {
  return new DeterministicOptimizationEngine().generateProposals(input)
}

export function remainingIssueCount(input: OptimizerInput): number {
  const reelSet = { id: 'optimizer', reels: input.reels }
  const validation = runConstraintEngine({
    reelSet,
    symbols: input.symbols,
    constraintDocument: input.constraintDocument,
  })
  return validation.summary.error + validation.summary.warning
}
