import type { ConstraintDocument } from '@/features/reel-studio/constraints/types'
import type { DesignGoals } from '@/features/reel-studio/generator/types'
import type { StudioReelStrip, StudioSymbol } from '@/features/reel-studio/types'

export type ProposalPriority = 'critical' | 'high' | 'medium' | 'low'

export type ProposalCategory =
  | 'balance'
  | 'distribution'
  | 'constraint'
  | 'spacing'
  | 'entropy'
  | 'inventory'
  | 'clustering'
  | 'feature'
  | 'volatility_preparation'
  | 'exposure_preparation'
  | 'rtp_preparation'

export type ProposalRisk = 'low' | 'medium' | 'high'

export type TimelineEventType = 'design' | 'generate' | 'optimize' | 'ready'

export interface ProposalPositionChange {
  reelIndex: number
  symbolIndex: number
  symbolId: string
}

export interface OptimizationProposal {
  id: string
  title: string
  description: string
  reason: string
  priority: ProposalPriority
  expectedImprovement: string[]
  affectedReels: number[]
  affectedSymbols: string[]
  before: ProposalPositionChange[]
  after: ProposalPositionChange[]
  healthGain: number
  confidence: number
  estimatedRisk: ProposalRisk
  category: ProposalCategory
  violationsFixed: number
  complexity: number
}

export interface GoalEvaluation {
  goalId: string
  label: string
  target: string
  current: string
  status: 'pass' | 'warning' | 'error'
  gap: number
}

export interface OptimizationIteration {
  id: string
  parentId: string | null
  branchLabel: string
  timestamp: number
  seed: number
  health: number
  healthDelta: number
  proposalId: string | null
  proposalTitle: string | null
  reels: StudioReelStrip[]
  distribution: Record<string, Record<number, number>>
  constraintSummary: { pass: number; warning: number; error: number }
  healthReasons: string[]
}

export interface TimelineEvent {
  id: string
  type: TimelineEventType
  timestamp: number
  seed: number
  iterationId: string
  health: number
  proposalId?: string
  label: string
}

export interface OptimizationReport {
  sessionId: string
  startedAt: number
  completedAt: number
  currentHealth: number
  newHealth: number
  improvement: number
  appliedProposals: string[]
  rejectedProposals: string[]
  remainingIssues: string[]
  estimatedNextImprovement: number
  timeSpentMs: number
}

export interface OptimizerInput {
  reels: StudioReelStrip[]
  symbols: Record<string, StudioSymbol>
  constraintDocument: ConstraintDocument
  designGoals: DesignGoals
  seed: number
}

export interface OptimizerOutput {
  proposals: OptimizationProposal[]
  goalEvaluation: GoalEvaluation[]
  currentHealth: number
}

export interface BatchOptimizationResult {
  applied: OptimizationProposal[]
  skipped: OptimizationProposal[]
  finalHealth: number
  finalReels: StudioReelStrip[]
  stoppedEarly: boolean
  report: OptimizationReport
}
