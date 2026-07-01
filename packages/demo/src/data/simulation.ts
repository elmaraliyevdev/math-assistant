import type { SimulationResults } from '@web/types/api'

import { DEMO_ENGINE_VERSION, DEMO_SIMULATION_ID, DEMO_VERSION_ID } from './constants'

/**
 * Realistic simulation results for Crown Quest v3.
 * Shape matches `SimulationResults` from the certified backend contract.
 */
export const demoSimulationResults: SimulationResults = {
  simulationId: DEMO_SIMULATION_ID,
  summary: {
    rtp: 0.9596,
    uncappedRtp: 0.9608,
    volatility: 4.18,
    hitFrequency: 0.281,
  },
  totals: {
    totalBetMinorUnits: 10_000_000_00,
    totalWinMinorUnits: 9_596_000_00,
  },
  featureFrequencies: [
    {
      featureName: 'Free Spins',
      triggerCount: 4218,
      frequency: 0.04218,
      oneInX: 23.7,
    },
    {
      featureName: 'Hold & Win',
      triggerCount: 892,
      frequency: 0.00892,
      oneInX: 112.1,
    },
  ],
  jackpotFrequencies: [
    {
      jackpotTier: 'Grand',
      triggerCount: 18,
      frequency: 0.00018,
      oneInX: 5555.6,
    },
  ],
  exposure: {
    truncationRate: 0.0082,
    totalTruncatedMinorUnits: 12_400_00,
    cappedRtp: 0.9596,
    uncappedRtp: 0.9608,
    rtpDifference: 0.0012,
    exposureCapApplied: true,
  },
  rtpDecomposition: {
    totalRtp: 0.9596,
    categories: [
      { rtpCategory: 'BASE', winMinorUnits: 6_912_000_00, rtpShare: 0.6912 },
      { rtpCategory: 'FREE_SPINS', winMinorUnits: 2_398_000_00, rtpShare: 0.2398 },
      { rtpCategory: 'HOLD_AND_WIN', winMinorUnits: 286_000_00, rtpShare: 0.0286 },
    ],
  },
  rtpValidation: {
    targetRtp: 96.0,
    actualRtp: 95.96,
    difference: -0.04,
    tolerance: 0.1,
    withinTolerance: true,
  },
  rtpDecompositionChart: {
    BASE: 69.12,
    FREE_SPINS: 23.98,
    HOLD_AND_WIN: 2.86,
    JACKPOT: 0.0,
    totalRtp: 95.96,
  },
  featureValidation: [
    {
      feature: 'FREE_SPINS',
      observedFrequency: 0.04218,
      expectedFrequency: 0.0420,
      difference: 0.00018,
      status: 'PASS',
    },
    {
      feature: 'HOLD_AND_WIN',
      observedFrequency: 0.00892,
      expectedFrequency: 0.0090,
      difference: -0.00008,
      status: 'PASS',
    },
  ],
  recommendations: [
    {
      severity: 'info',
      title: 'RTP within tolerance',
      description:
        'Observed RTP is 95.96% against a 96.0% target — within the 0.1 pp certification tolerance.',
    },
  ],
  confidenceInterval: {
    rtp: 0.9596,
    lowerBound: 0.9581,
    upperBound: 0.9611,
    confidenceLevel: 0.95,
  },
  winDistribution: {
    totalSpins: 10_000_000,
    betMinorUnitsPerSpin: 100,
    buckets: [
      { label: '0x', count: 7_190_000, percentage: 71.9 },
      { label: '0-1x', count: 1_050_000, percentage: 10.5 },
      { label: '1-2x', count: 820_000, percentage: 8.2 },
      { label: '2-5x', count: 510_000, percentage: 5.1 },
      { label: '5-10x', count: 280_000, percentage: 2.8 },
      { label: '10-25x', count: 98_000, percentage: 0.98 },
      { label: '25-50x', count: 38_000, percentage: 0.38 },
      { label: '50x+', count: 14_000, percentage: 0.14 },
    ],
  },
  volatilityMetrics: {
    meanWinMinorUnits: 96,
    variance: 17.47,
    standardDeviation: 4.18,
    coefficientOfVariation: 0.0435,
  },
  hitFrequency: {
    hitFrequency: 0.281,
    winningSpinCount: 2_810_000,
    losingSpinCount: 7_190_000,
  },
  engineVersion: DEMO_ENGINE_VERSION,
  gameVersionContentHash: 'c4a8f2e91b3d7c6e5a0f1d2b3c4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2',
  certificationNotice:
    'All displayed metrics originate from certified backend calculations.',
}
