import type { ConstraintDocument } from '@/features/reel-studio/constraints/types'
import type { StudioReelStrip, StudioSymbol } from '@/features/reel-studio/types'

export type VolatilityGoal = 'low' | 'medium' | 'high'
export type FeatureFrequencyGoal = 'low' | 'medium' | 'high'

export interface DesignGoals {
  targetRtpPercent: number
  volatility: VolatilityGoal
  hitRatePercent: number
  maximumWinMultiplier: number
  wildEveryNSymbols: number
  scatterEveryNSymbols: number
  freeSpinEveryNSpins: number
  featureFrequency: FeatureFrequencyGoal
  reelLength: number
  reelCount: number
}

export const DEFAULT_DESIGN_GOALS: DesignGoals = {
  targetRtpPercent: 96,
  volatility: 'medium',
  hitRatePercent: 28,
  maximumWinMultiplier: 5000,
  wildEveryNSymbols: 22,
  scatterEveryNSymbols: 45,
  freeSpinEveryNSpins: 180,
  featureFrequency: 'medium',
  reelLength: 64,
  reelCount: 5,
}

export interface GeneratorInput {
  reelCount: number
  reelLengths: number[]
  symbols: Record<string, StudioSymbol>
  constraintDocument: ConstraintDocument
  designGoals: DesignGoals
  seed: number
  candidateCount: number
  maxRepairIterations: number
}

export interface CandidateStatistics {
  entropy: number
  duplicatePercent: number
  symbolCounts: Record<string, number>
  reelLengths: number[]
}

export interface CandidateHeatmaps {
  wildClustering: Record<string, number>
  scatterSpacing: Record<string, number>
  violationIntensity: Record<string, number>
}

export interface GeneratedCandidate {
  id: string
  reels: StudioReelStrip[]
  qualityScore: number
  violations: number
  warnings: number
  statistics: CandidateStatistics
  heatmaps: CandidateHeatmaps
  distribution: Record<string, Record<number, number>>
  generationTimeMs: number
  seed: number
  repairCount: number
  summary: string
}

export interface GenerationReport {
  candidates: GeneratedCandidate[]
  generationTimeMs: number
  seed: number
  ranking: string[]
}

export interface CandidateDiffPosition {
  reelIndex: number
  symbolIndex: number
  before: string | null
  after: string | null
}

export interface DesignHealthMetric {
  id: string
  label: string
  score: number
  status: 'pass' | 'warning' | 'error'
  detail: string
}

export interface DesignHealthReport {
  overallScore: number
  metrics: DesignHealthMetric[]
  recommendations: string[]
}

export interface SmartSuggestion {
  id: string
  action: string
  fromReel: number
  fromPosition: number
  toReel: number
  toPosition: number
  symbolId: string
  expectedImprovements: string[]
}

export interface GeneratorStrategy {
  generate(input: GeneratorInput): GenerationReport
}
