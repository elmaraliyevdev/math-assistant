import type {
  CalibrateResponse,
  TheoreticalAnalysisResponse,
} from '@web/types/api'

import { DEMO_ENGINE_VERSION } from './constants'

export const demoTheoreticalAnalysis: TheoreticalAnalysisResponse = {
  rtp: {
    totalRtp: 0.9598,
    baseRtp: 0.6914,
    scatterRtp: 0.0482,
    lineRtp: 0.6914,
    outcomeCount: 3125,
    reelSetId: 'base_game',
  },
  featureProbabilities: [
    { trigger: 'FREE_SPINS', probability: 0.042, oneInX: 23.8 },
    { trigger: 'HOLD_AND_WIN', probability: 0.009, oneInX: 111.1 },
  ],
  engineVersion: DEMO_ENGINE_VERSION,
}

export const demoCalibrateResponse: CalibrateResponse = {
  theoreticalRtp: demoTheoreticalAnalysis.rtp,
  featureProbabilities: demoTheoreticalAnalysis.featureProbabilities,
  calibration: {
    targetRtp: 96.0,
    theoreticalRtp: 95.98,
    simulatedRtp: 95.96,
    targetDelta: -0.02,
    theoryVsSimulationDelta: -0.02,
    withinTolerance: true,
    tolerance: 0.1,
    rtpGapPp: 0.02,
    discrepancySeverity: 'ok',
    certificationStatus: 'cleared',
    certificationBlockThresholdPp: 25,
  },
  discrepancy: {
    summary:
      'Theoretical and simulated RTP are aligned within certification tolerance for Crown Quest v3.',
    items: [
      {
        metric: 'simulation_vs_theoretical_rtp',
        theoretical: 95.98,
        simulated: 95.96,
        target: 96.0,
        delta: -0.02,
        status: 'ok',
      },
      {
        metric: 'free_spins_trigger_rate',
        theoretical: 4.2,
        simulated: 4.218,
        target: null,
        delta: 0.018,
        status: 'ok',
      },
    ],
  },
  recommendations: [
    {
      severity: 'info',
      category: 'monitoring',
      action: 'Continue monitoring scatter spacing on reel 3 during the next iteration.',
      expectedRtpImpact: 'Negligible — within tolerance.',
      estimatedRtpContributionPp: 0,
      priority: 10,
      discrepancySeverity: 'ok',
    },
  ],
  certificationReadiness: {
    certificationStatus: 'cleared',
    blockingIssues: [],
    requiredActions: [],
    estimatedIterationsRemaining: 0,
  },
  engineVersion: DEMO_ENGINE_VERSION,
}
