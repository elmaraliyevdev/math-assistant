import type {
  BatchOptimizationResult,
  OptimizationProposal,
  OptimizerInput,
  OptimizerOutput,
} from '@/features/reel-studio/optimizer/optimizer-types'
import type { StudioReelStrip } from '@/features/reel-studio/types'

export interface OptimizationStrategy {
  generateProposals(input: OptimizerInput): OptimizerOutput
}

export interface ProposalApplicator {
  applyProposal(reels: StudioReelStrip[], proposal: OptimizationProposal): StudioReelStrip[]
  previewProposal(reels: StudioReelStrip[], proposal: OptimizationProposal): StudioReelStrip[]
}

export interface BatchOptimizer {
  optimizeBatch(
    input: OptimizerInput,
    proposals: OptimizationProposal[],
    count: number | 'all',
    sessionId: string,
    startedAt: number,
  ): BatchOptimizationResult
}
