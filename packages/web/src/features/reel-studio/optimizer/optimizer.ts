import { computeDesignHealth } from '@/features/reel-studio/generator/health'
import type { BatchOptimizer, OptimizationStrategy } from '@/features/reel-studio/optimizer/interfaces'
import { DeterministicOptimizationEngine } from '@/features/reel-studio/optimizer/optimization-engine'
import {
  buildOptimizationReport,
  estimateNextImprovement,
  summarizeRemainingIssues,
} from '@/features/reel-studio/optimizer/optimization-report'
import type {
  BatchOptimizationResult,
  OptimizationProposal,
  OptimizerInput,
  OptimizerOutput,
} from '@/features/reel-studio/optimizer/optimizer-types'
import { applyProposalToReels } from '@/features/reel-studio/optimizer/proposal-application'
import { rankProposals } from '@/features/reel-studio/optimizer/proposal-ranking'

export class DeterministicOptimizer implements OptimizationStrategy {
  private readonly engine: OptimizationStrategy

  constructor(engine: OptimizationStrategy = new DeterministicOptimizationEngine()) {
    this.engine = engine
  }

  generateProposals(input: OptimizerInput): OptimizerOutput {
    return this.engine.generateProposals(input)
  }
}

export class DefaultBatchOptimizer implements BatchOptimizer {
  optimizeBatch(
    input: OptimizerInput,
    proposals: OptimizationProposal[],
    count: number | 'all',
    sessionId: string,
    startedAt: number,
  ): BatchOptimizationResult {
    const ranked = rankProposals(proposals)
    const limit = count === 'all' ? ranked.length : count
    const selected = ranked.slice(0, limit)

    let reels = input.reels.map((reel) => ({ ...reel, symbols: [...reel.symbols] }))
    const beforeSet = { id: 'batch-before', reels }
    const applied: OptimizationProposal[] = []
    const skipped: OptimizationProposal[] = []
    let stoppedEarly = false

    for (const proposal of selected) {
      const currentSet = { id: 'batch-current', reels }
      const currentHealth = computeDesignHealth(
        currentSet,
        input.symbols,
        input.constraintDocument,
      ).overallScore
      const nextReels = applyProposalToReels(reels, proposal)
      const nextSet = { id: 'batch-next', reels: nextReels }
      const nextHealth = computeDesignHealth(
        nextSet,
        input.symbols,
        input.constraintDocument,
      ).overallScore
      if (nextHealth < currentHealth) {
        skipped.push(proposal)
        stoppedEarly = true
        break
      }
      reels = nextReels
      applied.push(proposal)
    }

    const afterSet = { id: 'batch-after', reels }
    const finalHealth = computeDesignHealth(
      afterSet,
      input.symbols,
      input.constraintDocument,
    ).overallScore
    const remaining = rankProposals(
      new DeterministicOptimizer().generateProposals({ ...input, reels }).proposals,
    )

    const report = buildOptimizationReport({
      sessionId,
      startedAt,
      completedAt: Date.now(),
      beforeReelSet: beforeSet,
      afterReelSet: afterSet,
      symbols: input.symbols,
      constraintDocument: input.constraintDocument,
      appliedProposals: applied,
      rejectedProposalIds: skipped.map((proposal) => proposal.id),
      remainingIssues: summarizeRemainingIssues(remaining, []),
      estimatedNextImprovement: estimateNextImprovement(remaining),
    })

    return {
      applied,
      skipped,
      finalHealth,
      finalReels: reels,
      stoppedEarly,
      report,
    }
  }
}

export function optimize(input: OptimizerInput): OptimizerOutput {
  return new DeterministicOptimizer().generateProposals(input)
}

export function optimizeBatch(
  input: OptimizerInput,
  count: number | 'all',
  sessionId: string,
  startedAt: number,
): BatchOptimizationResult {
  const output = optimize(input)
  return new DefaultBatchOptimizer().optimizeBatch(
    input,
    output.proposals,
    count,
    sessionId,
    startedAt,
  )
}
