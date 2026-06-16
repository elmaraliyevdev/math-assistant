import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { CalibrationDashboard } from '@/features/mathematics/components/CalibrationDashboard'
import { CertificationReportViewer } from '@/features/mathematics/components/CertificationReportViewer'
import { RtpGaugeChart } from '@/features/mathematics/components/RtpGaugeChart'
import { TheoreticalRtpPanel } from '@/features/mathematics/components/TheoreticalRtpPanel'
import type { CalibrateResponse, CertificationReportResponse, TheoreticalAnalysisResponse } from '@/types/api'

const theoreticalData: TheoreticalAnalysisResponse = {
  rtp: {
    totalRtp: 0.0512,
    baseRtp: 0.0512,
    scatterRtp: 0,
    lineRtp: 0.0512,
    outcomeCount: 3125,
    reelSetId: 'base_game',
  },
  featureProbabilities: [
    { trigger: 'FREE_SPINS', probability: 0.027, oneInX: 37.04 },
  ],
  engineVersion: 'runtime-core@1.8.0',
}

const calibrateData: CalibrateResponse = {
  theoreticalRtp: theoreticalData.rtp,
  featureProbabilities: theoreticalData.featureProbabilities,
  calibration: {
    targetRtp: 96,
    theoreticalRtp: 5.12,
    simulatedRtp: 5.1,
    targetDelta: -90.88,
    theoryVsSimulationDelta: -0.02,
    withinTolerance: false,
    tolerance: 0.1,
  },
  discrepancy: {
    summary: 'Metrics outside tolerance.',
    items: [
      {
        metric: 'simulation_vs_theoretical_rtp',
        theoretical: 5.12,
        simulated: 5.1,
        target: null,
        delta: -0.02,
        status: 'ok',
      },
    ],
  },
  recommendations: [
    {
      severity: 'warning',
      category: 'paytable',
      action: 'Increase H1 5OAK multiplier from 100x to 120x.',
      expectedRtpImpact: 'Estimated +2.0 percentage points toward target RTP.',
    },
  ],
  engineVersion: 'runtime-core@1.8.0',
}

const certificationData: CertificationReportResponse = {
  gameVersionId: 'version-1',
  gameTitle: 'Base 5x3',
  targetRtp: 96,
  theoreticalRtp: theoreticalData.rtp,
  simulatedRtp: 5.12,
  rtpVariance: 0.02,
  featureProbabilities: theoreticalData.featureProbabilities,
  exposure: {
    maxWinMinorUnits: 500000,
    maxWinMultiplier: 5000,
    capScope: 'session_spin_chain',
  },
  calibration: calibrateData.calibration,
  discrepancy: calibrateData.discrepancy,
  recommendations: calibrateData.recommendations,
  engineVersion: 'runtime-core@1.8.0',
}

describe('Mathematics workbench components', () => {
  it('renders theoretical RTP breakdown', () => {
    render(<TheoreticalRtpPanel data={theoreticalData} />)
    expect(screen.getByText('Theoretical RTP')).toBeInTheDocument()
    expect(screen.getByText('FREE_SPINS')).toBeInTheDocument()
    expect(screen.getByText('3,125')).toBeInTheDocument()
  })

  it('renders calibration gauges and recommendations', () => {
    render(<CalibrationDashboard data={calibrateData} />)
    expect(screen.getByText('Target RTP')).toBeInTheDocument()
    expect(screen.getByText('Increase H1 5OAK multiplier from 100x to 120x.')).toBeInTheDocument()
  })

  it('renders certification preview and download actions', () => {
    render(
      <CertificationReportViewer
        report={certificationData}
        onDownload={() => undefined}
      />,
    )
    expect(screen.getByText('Certification Report Preview')).toBeInTheDocument()
    expect(screen.getByText('Download PDF')).toBeInTheDocument()
    expect(screen.getByText(/Base 5x3/)).toBeInTheDocument()
  })

  it('renders RTP gauge value', () => {
    render(<RtpGaugeChart label="Theoretical RTP" value={5.12} />)
    expect(screen.getByText('5.12%')).toBeInTheDocument()
  })
})
