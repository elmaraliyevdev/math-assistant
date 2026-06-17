export interface User {
  id: string
  email: string
  fullName: string
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface TokenResponse {
  accessToken: string
  refreshToken: string
  tokenType: string
  expiresIn: number
}

export interface RegisterResponse {
  user: User
  organizationId: string
  tokens: TokenResponse
}

export interface OrganizationMembership {
  organizationId: string
  organizationName: string
  organizationSlug: string
  role: OrganizationRole
}

export type OrganizationRole = 'owner' | 'admin' | 'developer' | 'viewer'

export interface MeResponse {
  user: User
  organizations: OrganizationMembership[]
}

export interface Organization {
  id: string
  name: string
  slug: string
  createdAt: string
  updatedAt: string
}

export interface OrganizationListResponse {
  items: Organization[]
}

export interface OrganizationMember {
  userId: string
  organizationId: string
  role: OrganizationRole
  email?: string | null
  fullName?: string | null
}

export interface OrganizationMemberListResponse {
  items: OrganizationMember[]
}

export interface OrganizationInvitation {
  id: string
  organizationId: string
  organizationName: string
  email: string
  role: OrganizationRole
  status: 'pending' | 'accepted' | 'declined' | 'expired' | 'cancelled'
  invitedByUserId: string
  expiresAt: string
  createdAt: string
  acceptedAt?: string | null
}

export interface OrganizationInvitationListResponse {
  items: OrganizationInvitation[]
}

export interface EngineVersion {
  engineVersion: string
  validatorVersion: string
  supportedPlugins: Array<{ pluginId: string; version: string }>
  rng: { algorithm: string; policy: string }
  maxRecommendedSpinCount: number
  deploymentMode: string
  maxSimulationSpinCount: number
  maxActiveSimulations: number | null
  activeSimulationCount: number
}

export interface Game {
  id: string
  organizationId: string
  name: string
  description: string | null
  createdAt: string
  updatedAt: string
}

export interface GameListResponse {
  items: Game[]
  total: number
  page: number
  pageSize: number
}

export interface GameVersionSummary {
  id: string
  version: number
  contentHash: string
  engineVersion: string
  createdAt: string
}

export interface ValidationFinding {
  code: string
  severity: string
  message: string
  path: string
  suggestion: string | null
}

export interface ValidationSummary {
  passed: boolean
  findingCount: number
  findings: ValidationFinding[]
}

export interface GameVersionDetail extends GameVersionSummary {
  canonicalJson: Record<string, unknown>
  validationSummary: ValidationSummary
}

export interface CreateGameVersionResponse {
  id: string
  version: number
  contentHash: string
  engineVersion: string
  validationSummary: ValidationSummary
}

export interface SimulationSummary {
  id: string
  gameVersionId: string
  status: string
  spinCount: number
  completedSpinCount: number
  createdAt: string
  completedAt: string | null
  errorMessage: string | null
}

export interface SimulationListResponse {
  items: SimulationSummary[]
  total: number
  page: number
  pageSize: number
}

export interface SimulationProgress {
  completedSpins: number
  percentage: number
}

export interface SimulationDetail {
  id: string
  gameVersionId: string
  status: string
  spinCount: number
  completedSpinCount: number
  betMinorUnits: number
  eventLogMode: string
  createdAt: string
  startedAt: string | null
  completedAt: string | null
  cancelRequested: boolean
  workerId: string | null
  errorMessage: string | null
  progress: SimulationProgress
  totalShards?: number
  completedShards?: number
  failedShards?: number
  progressPercentage?: number
  distributedExecution?: boolean
}

export interface SimulationResults {
  simulationId: string
  summary: {
    rtp: number
    uncappedRtp: number
    volatility: number
    hitFrequency: number
  }
  totals: {
    totalBetMinorUnits: number
    totalWinMinorUnits: number
  }
  featureFrequencies: Array<{
    featureName: string
    triggerCount: number
    frequency: number
    oneInX: number | null
  }>
  jackpotFrequencies: Array<{
    jackpotTier: string
    triggerCount: number
    frequency: number
    oneInX: number | null
  }>
  exposure: {
    truncationRate: number
    totalTruncatedMinorUnits: number
    cappedRtp: number
    uncappedRtp: number
    rtpDifference: number
    exposureCapApplied: boolean
  }
  rtpDecomposition: {
    totalRtp: number
    categories: Array<{
      rtpCategory: string
      winMinorUnits: number
      rtpShare: number
    }>
  }
  rtpValidation: {
    targetRtp: number
    actualRtp: number
    difference: number
    tolerance: number
    withinTolerance: boolean
  } | null
  rtpDecompositionChart: {
    BASE: number
    FREE_SPINS: number
    HOLD_AND_WIN: number
    JACKPOT: number
    totalRtp: number
  }
  featureValidation: Array<{
    feature: string
    observedFrequency: number
    expectedFrequency: number
    difference: number
    status: string
  }>
  recommendations: Array<{
    severity: string
    title: string
    description: string
  }>
  confidenceInterval: {
    rtp: number
    lowerBound: number
    upperBound: number
    confidenceLevel: number
  }
  winDistribution: {
    totalSpins: number
    betMinorUnitsPerSpin: number
    buckets: Array<{
      label: string
      count: number
      percentage: number
    }>
  }
  volatilityMetrics: {
    meanWinMinorUnits: number
    variance: number
    standardDeviation: number
    coefficientOfVariation: number | null
  }
  hitFrequency: {
    hitFrequency: number
    winningSpinCount: number
    losingSpinCount: number
  }
  engineVersion: string
  gameVersionContentHash: string
  certificationNotice: string
}

export interface SimulationNote {
  id: string
  simulationId: string
  authorId: string
  content: string
  createdAt: string
}

export interface SimulationNoteListResponse {
  items: SimulationNote[]
}

export interface SimulationCompareEntry {
  simulationId: string
  gameName?: string | null
  gameVersionLabel?: string | null
  detail: SimulationDetail
  results: SimulationResults
  runtimeDurationMs: number | null
}

export interface SimulationThroughput {
  spinsPerSecond: number
  sampleCount: number
  source: string
}

export interface SimulationCompareResponse {
  simulations: SimulationCompareEntry[]
  comparison: {
    rtp: Array<{ simulationId: string; value: number }>
    volatility: Array<{ simulationId: string; value: number }>
    hitFrequency: Array<{ simulationId: string; value: number }>
    confidenceIntervals: Array<{
      simulationId: string
      lowerBound: number
      upperBound: number
      confidenceLevel: number
    }>
    featureFrequency: Array<{
      simulationId: string
      featureName: string
      frequency: number
    }>
    rtpDecomposition: Array<{
      simulationId: string
      BASE: number
      FREE_SPINS: number
      HOLD_AND_WIN: number
      JACKPOT: number
      totalRtp: number
    }>
  }
}

export interface MathConfigSnapshot {
  rtpTarget: { percent: number; tolerance?: number } | null
  scatterTriggers: Array<{
    state: string
    symbolId: string
    minCount: number
    emitTrigger: string
  }>
  bonusTriggers: Array<{
    state: string
    symbolId: string
    minCount: number
    emitTrigger: string
  }>
  jackpotTiers: Record<string, number>
  exposureCap: {
    maxWinMinorUnits: number | null
    maxWinMultiplier: number | null
  }
  paytableSummary: Array<{
    symbolId: string
    count: number
    multiplier: number
  }>
}

export interface ApiErrorBody {
  error: {
    code: string
    message: string
  }
}

export interface TheoreticalRtp {
  totalRtp: number
  baseRtp: number
  scatterRtp: number
  lineRtp: number
  outcomeCount: number
  reelSetId: string
}

export interface FeatureProbability {
  trigger: string
  probability: number
  oneInX: number | null
}

export interface TheoreticalAnalysisResponse {
  rtp: TheoreticalRtp
  featureProbabilities: FeatureProbability[]
  engineVersion: string
}

export interface CalibrationResult {
  targetRtp: number | null
  theoreticalRtp: number
  simulatedRtp: number | null
  targetDelta: number | null
  theoryVsSimulationDelta: number | null
  withinTolerance: boolean | null
  tolerance: number | null
  rtpGapPp: number | null
  discrepancySeverity: string | null
  certificationStatus: string | null
  certificationBlockThresholdPp: number | null
}

export interface DiscrepancyItem {
  metric: string
  theoretical: number | null
  simulated: number | null
  target: number | null
  delta: number
  status: string
}

export interface DiscrepancyAnalysis {
  items: DiscrepancyItem[]
  summary: string
}

export interface CalibrationRecommendation {
  severity: string
  category: string
  action: string
  expectedRtpImpact: string
  estimatedRtpContributionPp: number
  priority: number
  discrepancySeverity: string
  estimatedVolatilityImpact?: string | null
  exposureImpact?: string | null
}

export interface CertificationReadinessSummary {
  certificationStatus: string
  blockingIssues: string[]
  requiredActions: string[]
  estimatedIterationsRemaining: number
}

export interface CalibrateResponse {
  theoreticalRtp: TheoreticalRtp
  featureProbabilities: FeatureProbability[]
  calibration: CalibrationResult
  discrepancy: DiscrepancyAnalysis
  recommendations: CalibrationRecommendation[]
  certificationReadiness: CertificationReadinessSummary
  engineVersion: string
}

export interface CertificationReportResponse {
  gameVersionId: string
  gameTitle: string
  targetRtp: number | null
  theoreticalRtp: TheoreticalRtp
  simulatedRtp: number | null
  rtpVariance: number | null
  featureProbabilities: FeatureProbability[]
  exposure: {
    maxWinMinorUnits: number
    maxWinMultiplier: number | null
    capScope: string
  }
  calibration: CalibrationResult | null
  discrepancy: DiscrepancyAnalysis | null
  recommendations: CalibrationRecommendation[]
  certificationReadiness?: CertificationReadinessSummary | null
  engineVersion: string
}

export interface GroundedCitation {
  label: string
  source: string
  path: string
  value?: string | number | null
}

export interface AssistantSection {
  title: string
  content: string
}

export interface AssistantResponse {
  content: string
  sections: AssistantSection[]
  citations: GroundedCitation[]
}

export interface SimulationAnalysisResponse extends AssistantResponse {
  simulationId: string
}

export interface SimulationRecommendResponse extends AssistantResponse {
  simulationId: string
  targetRtp: number | null
  recommendations: CalibrationRecommendation[]
}

export interface SimulationCompareAssistantResponse extends AssistantResponse {
  simulationIds: string[]
}

export interface GameVersionExplainResponse extends AssistantResponse {
  gameVersionId: string
}

export interface PaginationParams {
  page?: number
  pageSize?: number
  search?: string
}
