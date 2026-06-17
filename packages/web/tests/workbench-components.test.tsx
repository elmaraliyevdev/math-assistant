import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import { CalibrationDashboard } from '@/features/workbench/components/CalibrationDashboard'
import { ComparisonDeltaSummary } from '@/features/workbench/components/ComparisonDeltaSummary'
import { FieldHelp, FieldLabel } from '@/features/workbench/components/FieldHelp'
import { RuntimeEstimateNotice } from '@/features/workbench/components/RuntimeEstimateNotice'
import { SpinCountPresets } from '@/features/workbench/components/SpinCountPresets'
import { TuningRecommendationsPanel } from '@/features/workbench/components/TuningRecommendationsPanel'
import type { CalibrateResponse, SimulationCompareResponse } from '@/types/api'
import { certifiedSimulationResults } from './fixtures/certified-results'
import { renderWithQuery } from './test-utils'

const compareData: SimulationCompareResponse = {
  simulations: [
    {
      simulationId: 'sim-1',
      gameName: 'Lucky Stars',
      gameVersionLabel: 'v1',
      runtimeDurationMs: 1000,
      detail: {
        id: 'sim-1',
        gameVersionId: 'version-1',
        status: 'completed',
        spinCount: 1000,
        completedSpinCount: 1000,
        betMinorUnits: 100,
        eventLogMode: 'none',
        createdAt: '2026-01-01T00:00:00Z',
        startedAt: '2026-01-01T00:00:01Z',
        completedAt: '2026-01-01T00:00:02Z',
        cancelRequested: false,
        workerId: null,
        errorMessage: null,
        progress: { completedSpins: 1000, percentage: 100 },
      },
      results: {
        ...certifiedSimulationResults,
        simulationId: 'sim-1',
        summary: { ...certifiedSimulationResults.summary, rtp: 0.96, volatility: 4, hitFrequency: 0.3 },
      },
    },
    {
      simulationId: 'sim-2',
      gameName: 'Lucky Stars',
      gameVersionLabel: 'v2',
      runtimeDurationMs: 1200,
      detail: {
        id: 'sim-2',
        gameVersionId: 'version-2',
        status: 'completed',
        spinCount: 1000,
        completedSpinCount: 1000,
        betMinorUnits: 100,
        eventLogMode: 'none',
        createdAt: '2026-01-02T00:00:00Z',
        startedAt: '2026-01-02T00:00:01Z',
        completedAt: '2026-01-02T00:00:02Z',
        cancelRequested: false,
        workerId: null,
        errorMessage: null,
        progress: { completedSpins: 1000, percentage: 100 },
      },
      results: {
        ...certifiedSimulationResults,
        simulationId: 'sim-2',
        summary: { ...certifiedSimulationResults.summary, rtp: 0.94, volatility: 4.5, hitFrequency: 0.28 },
        featureFrequencies: [{ featureName: 'Free Spins', triggerCount: 1, frequency: 0.03, oneInX: 33 }],
      },
    },
  ],
  comparison: {
    rtp: [],
    volatility: [],
    hitFrequency: [],
    confidenceIntervals: [],
    featureFrequency: [],
    rtpDecomposition: [],
  },
}

const calibrateData: CalibrateResponse = {
  theoreticalRtp: {
    totalRtp: 0.96,
    baseRtp: 0.5,
    scatterRtp: 0.46,
    lineRtp: 0.5,
    outcomeCount: 1000,
    reelSetId: 'base',
  },
  featureProbabilities: [],
  calibration: {
    targetRtp: 96,
    theoreticalRtp: 96,
    simulatedRtp: 95.5,
    targetDelta: -0.5,
    theoryVsSimulationDelta: -0.5,
    withinTolerance: false,
    tolerance: 0.1,
    rtpGapPp: 0.5,
    discrepancySeverity: 'minor',
    certificationStatus: 'cleared',
    certificationBlockThresholdPp: 25,
  },
  discrepancy: {
    summary: 'Outside tolerance.',
    items: [
      {
        metric: 'RTP',
        theoretical: 96,
        simulated: 95.5,
        target: 96,
        delta: -0.5,
        status: 'FAIL',
      },
      {
        metric: 'FREE_SPINS Frequency',
        theoretical: 0.03,
        simulated: 0.028,
        target: 0.03,
        delta: -0.002,
        status: 'PASS',
      },
      {
        metric: 'Max Exposure',
        theoretical: 5000,
        simulated: 4800,
        target: null,
        delta: -200,
        status: 'PASS',
      },
    ],
  },
  recommendations: [],
  certificationReadiness: {
    certificationStatus: 'cleared',
    blockingIssues: [],
    requiredActions: [],
    estimatedIterationsRemaining: 0,
  },
  engineVersion: 'runtime-core@1.8.0',
}

describe('workbench components', () => {
  it('renders comparison delta summary', () => {
    render(<ComparisonDeltaSummary data={compareData} />)
    expect(screen.getByText(/delta metrics/i)).toBeInTheDocument()
    expect(screen.getByText('Lucky Stars v1')).toBeInTheDocument()
    expect(screen.getAllByText('baseline').length).toBeGreaterThan(0)
  })

  it('renders runtime estimate from historical throughput', () => {
    render(
      <RuntimeEstimateNotice
        spinCount={100_000}
        spinsPerSecond={50_000}
        source="historical"
        sampleCount={3}
      />,
    )
    expect(screen.getByText(/estimated runtime/i)).toBeInTheDocument()
    expect(screen.getByText(/3 completed simulation/i)).toBeInTheDocument()
  })

  it('hides runtime estimate when throughput is unavailable', () => {
    const { container } = render(<RuntimeEstimateNotice spinCount={1000} />)
    expect(container).toBeEmptyDOMElement()
  })

  it('renders deployment fallback runtime estimate', () => {
    render(
      <RuntimeEstimateNotice
        spinCount={50_000}
        spinsPerSecond={50_000}
        source="deployment_fallback"
      />,
    )
    expect(screen.getByText(/deployment fallback throughput/i)).toBeInTheDocument()
  })

  it('renders spin count presets and selects a value', async () => {
    const user = userEvent.setup()
    let selected = 1000
    render(
      <SpinCountPresets
        value={selected}
        maxSpinCount={1_000_000}
        onSelect={(value) => {
          selected = value
        }}
      />,
    )
    await user.click(screen.getByRole('button', { name: '100K' }))
    expect(selected).toBe(100_000)
    expect(screen.getByRole('button', { name: '10M' })).toBeDisabled()
  })

  it('renders field label with help tooltip', () => {
    render(
      <>
        <FieldLabel
          htmlFor="field-id"
          label="Spin count"
          description="Use higher spin counts for calibration."
        />
        <input id="field-id" aria-label="Spin count input" />
      </>,
    )
    expect(screen.getByText('Spin count')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /show help/i })).toBeInTheDocument()
    render(<FieldHelp description="Standalone help" />)
    expect(screen.getAllByRole('button', { name: /show help/i })).toHaveLength(2)
  })

  it('renders calibration dashboard states', () => {
    const { rerender } = render(<CalibrationDashboard isLoading />)
    expect(document.querySelector('.animate-pulse')).toBeTruthy()

    rerender(<CalibrationDashboard error="Calibration failed" />)
    expect(screen.getByText(/calibration failed/i)).toBeInTheDocument()

    rerender(<CalibrationDashboard data={calibrateData} />)
    expect(screen.getByText('RTP')).toBeInTheDocument()
    expect(screen.getByText('FAIL')).toBeInTheDocument()
    expect(screen.getAllByText('PASS')).toHaveLength(2)
  })

  it('renders empty tuning recommendations', () => {
    renderWithQuery(
      <TuningRecommendationsPanel simulationId="sim-1" recommendations={[]} />,
    )
    expect(screen.getByText(/no tuning recommendations/i)).toBeInTheDocument()
  })

  it('tracks tuning recommendation decisions', async () => {
    const user = userEvent.setup()
    renderWithQuery(
      <TuningRecommendationsPanel
        simulationId="sim-tuning"
        recommendations={[
          {
            severity: 'warning',
            title: 'Reduce SCATTER frequency',
            description: 'Lower trigger rate on reel 3.',
          },
        ]}
      />,
    )
    expect(screen.getByText(/reduce scatter frequency/i)).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Accept' }))
    expect(screen.getByText('accepted')).toBeInTheDocument()
    await user.type(
      screen.getByPlaceholderText(/add a note for this recommendation/i),
      'Will update reel weights',
    )
    expect(screen.getByDisplayValue(/will update reel weights/i)).toBeInTheDocument()
  })
})
