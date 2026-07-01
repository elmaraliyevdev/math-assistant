import type { CertificationReportResponse } from '@web/types/api'

import { demoCalibrateResponse } from './mathematics'
import { DEMO_ENGINE_VERSION, DEMO_VERSION_ID } from './constants'
import { demoGame } from './games'

export const demoCertificationReport: CertificationReportResponse = {
  gameVersionId: DEMO_VERSION_ID,
  gameTitle: demoGame.name,
  targetRtp: 96.0,
  theoreticalRtp: demoCalibrateResponse.theoreticalRtp,
  simulatedRtp: 95.96,
  rtpVariance: 0.018,
  featureProbabilities: demoCalibrateResponse.featureProbabilities,
  exposure: {
    maxWinMinorUnits: 500_000_00,
    maxWinMultiplier: 5000,
    capScope: 'session_spin_chain',
  },
  calibration: demoCalibrateResponse.calibration,
  discrepancy: demoCalibrateResponse.discrepancy,
  recommendations: demoCalibrateResponse.recommendations,
  certificationReadiness: demoCalibrateResponse.certificationReadiness,
  engineVersion: DEMO_ENGINE_VERSION,
}

/** Approval workflow stages shown in certification demos. */
export const demoCertificationStages = [
  { stage: 'Mathematician', status: 'completed' as const, date: 'Jun 12' },
  { stage: 'Senior mathematician', status: 'completed' as const, date: 'Jun 14' },
  { stage: 'Product owner', status: 'completed' as const, date: 'Jun 15' },
  { stage: 'Producer', status: 'pending' as const },
] as const

export const demoReviewComments = [
  {
    author: 'Elena K.',
    role: 'Mathematician',
    content:
      'Scatter frequency on reel 3 adjusted — observed trigger rate now within 0.02 pp of theoretical.',
    time: '2h ago',
  },
  {
    author: 'Marcus T.',
    role: 'Senior mathematician',
    content:
      'RTP gap cleared. Volatility index matches spec. Ready for producer sign-off.',
    time: '45m ago',
  },
] as const
