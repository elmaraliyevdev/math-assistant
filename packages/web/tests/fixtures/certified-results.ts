import type { SimulationResults } from '@/types/api'

/** Backend-certified fields for component tests (no client-side math). */
export const certifiedSimulationResults: SimulationResults = {
  simulationId: 'sim-1',
  summary: {
    rtp: 0.96,
    uncappedRtp: 0.97,
    volatility: 4.2,
    hitFrequency: 0.28,
  },
  totals: {
    totalBetMinorUnits: 100_000,
    totalWinMinorUnits: 96_000,
  },
  featureFrequencies: [
    {
      featureName: 'Free Spins',
      triggerCount: 42,
      frequency: 0.042,
      oneInX: 23.8,
    },
  ],
  jackpotFrequencies: [
    {
      jackpotTier: 'Grand',
      triggerCount: 2,
      frequency: 0.002,
      oneInX: 500,
    },
  ],
  exposure: {
    truncationRate: 0.01,
    totalTruncatedMinorUnits: 100,
    cappedRtp: 0.96,
    uncappedRtp: 0.97,
    rtpDifference: 0.01,
    exposureCapApplied: true,
  },
  rtpDecomposition: {
    totalRtp: 0.96,
    categories: [
      { rtpCategory: 'BASE', winMinorUnits: 10_000, rtpShare: 0.1 },
      { rtpCategory: 'FREE_SPINS', winMinorUnits: 86_000, rtpShare: 0.86 },
    ],
  },
  rtpValidation: {
    targetRtp: 96.0,
    actualRtp: 95.91,
    difference: -0.09,
    tolerance: 0.1,
    withinTolerance: true,
  },
  rtpDecompositionChart: {
    BASE: 10.0,
    FREE_SPINS: 86.0,
    HOLD_AND_WIN: 0.0,
    JACKPOT: 0.0,
    totalRtp: 96.0,
  },
  featureValidation: [
    {
      feature: 'FREE_SPINS',
      observedFrequency: 0.684,
      expectedFrequency: 0.683,
      difference: 0.001,
      status: 'PASS',
    },
  ],
  recommendations: [
    {
      severity: 'warning',
      title: 'Low Base RTP',
      description: 'Base RTP contributes only 5.2%.',
    },
  ],
  confidenceInterval: {
    rtp: 0.96,
    lowerBound: 0.92,
    upperBound: 1.0,
    confidenceLevel: 0.95,
  },
  winDistribution: {
    totalSpins: 1000,
    betMinorUnitsPerSpin: 100,
    buckets: [
      { label: '0x', count: 720, percentage: 72 },
      { label: '0-1x', count: 100, percentage: 10 },
      { label: '1-2x', count: 80, percentage: 8 },
      { label: '2-5x', count: 50, percentage: 5 },
      { label: '5-10x', count: 30, percentage: 3 },
      { label: '10-25x', count: 12, percentage: 1.2 },
      { label: '25-50x', count: 5, percentage: 0.5 },
      { label: '50x+', count: 3, percentage: 0.3 },
    ],
  },
  volatilityMetrics: {
    meanWinMinorUnits: 96,
    variance: 17.64,
    standardDeviation: 4.2,
    coefficientOfVariation: 0.04375,
  },
  hitFrequency: {
    hitFrequency: 0.28,
    winningSpinCount: 280,
    losingSpinCount: 720,
  },
  engineVersion: 'runtime-core@1.8.0',
  gameVersionContentHash: 'a'.repeat(64),
  certificationNotice:
    'All displayed metrics originate from certified backend calculations.',
}
