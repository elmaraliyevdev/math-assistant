import { computeDesignHealth } from '@/features/reel-studio/generator/health'
import type {
  OptimizationProposal,
  OptimizationReport,
} from '@/features/reel-studio/optimizer/optimizer-types'
import type { ConstraintDocument } from '@/features/reel-studio/constraints/types'
import type { StudioReelSet, StudioSymbol } from '@/features/reel-studio/types'

export function buildOptimizationReport(options: {
  sessionId: string
  startedAt: number
  completedAt: number
  beforeReelSet: StudioReelSet
  afterReelSet: StudioReelSet
  symbols: Record<string, StudioSymbol>
  constraintDocument: ConstraintDocument
  appliedProposals: OptimizationProposal[]
  rejectedProposalIds: string[]
  remainingIssues: string[]
  estimatedNextImprovement: number
}): OptimizationReport {
  const currentHealth = computeDesignHealth(
    options.beforeReelSet,
    options.symbols,
    options.constraintDocument,
  ).overallScore
  const newHealth = computeDesignHealth(
    options.afterReelSet,
    options.symbols,
    options.constraintDocument,
  ).overallScore

  return {
    sessionId: options.sessionId,
    startedAt: options.startedAt,
    completedAt: options.completedAt,
    currentHealth,
    newHealth,
    improvement: newHealth - currentHealth,
    appliedProposals: options.appliedProposals.map((proposal) => proposal.id),
    rejectedProposals: options.rejectedProposalIds,
    remainingIssues: options.remainingIssues,
    estimatedNextImprovement: options.estimatedNextImprovement,
    timeSpentMs: options.completedAt - options.startedAt,
  }
}

export function summarizeRemainingIssues(
  proposals: OptimizationProposal[],
  rejectedIds: string[],
): string[] {
  return proposals
    .filter((proposal) => !rejectedIds.includes(proposal.id))
    .slice(0, 5)
    .map((proposal) => proposal.reason)
}

export function estimateNextImprovement(proposals: OptimizationProposal[]): number {
  if (proposals.length === 0) {
    return 0
  }
  return Math.max(...proposals.map((proposal) => proposal.healthGain))
}
