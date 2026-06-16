import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { MathConfigurationSnapshot } from '@/features/simulations/components/MathConfigurationSnapshot'
import { SimulationComparisonWorkbench } from '@/features/simulations/components/SimulationComparisonWorkbench'
import {
  deriveComparisonHighlights,
  extractMathConfigSnapshot,
  formatDurationMs,
} from '@/features/simulations/utils/workbench'
import type { SimulationCompareResponse } from '@/types/api'

const canonicalJson = {
  metadata: { rtpTarget: { percent: 96, tolerance: 0.1 } },
  stateMachines: {
    main: {
      states: {
        BASE: {
          scatterTriggers: [
            {
              symbolId: 'SCATTER',
              minCount: 3,
              emitTrigger: 'FREE_SPINS',
            },
          ],
          bonusTriggers: [],
        },
      },
    },
  },
  paytable: {
    pays: [{ symbolId: 'H1', count: 5, multiplier: 100 }],
  },
  runtimeLimits: {
    exposure: { maxWinMinorUnits: 500000, maxWinMultiplier: 5000 },
  },
}

const compareData: SimulationCompareResponse = {
  simulations: [
    {
      simulationId: 'sim-1',
      runtimeDurationMs: 1500,
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
        workerId: 'worker-1',
        errorMessage: null,
        progress: { completedSpins: 1000, percentage: 100 },
      },
      results: {
        simulationId: 'sim-1',
        summary: { rtp: 0.51, uncappedRtp: 0.51, volatility: 4, hitFrequency: 0.2 },
        totals: { totalBetMinorUnits: 100000, totalWinMinorUnits: 51000 },
        featureFrequencies: [
          { featureName: 'FREE_SPINS', triggerCount: 684, frequency: 0.684, oneInX: 1.5 },
        ],
        jackpotFrequencies: [],
        exposure: {
          truncationRate: 0,
          totalTruncatedMinorUnits: 0,
          cappedRtp: 0.51,
          uncappedRtp: 0.51,
          rtpDifference: 0,
          exposureCapApplied: false,
        },
        confidenceInterval: {
          rtp: 0.51,
          lowerBound: 0.48,
          upperBound: 0.54,
          confidenceLevel: 0.95,
        },
        winDistribution: {
          totalSpins: 1000,
          betMinorUnitsPerSpin: 100,
          buckets: [{ label: '0x', count: 800, percentage: 80 }],
        },
        volatilityMetrics: {
          meanWinMinorUnits: 51,
          variance: 16,
          standardDeviation: 4,
          coefficientOfVariation: 0.078,
        },
        hitFrequency: {
          hitFrequency: 0.2,
          winningSpinCount: 200,
          losingSpinCount: 800,
        },
        engineVersion: 'runtime-core@1.8.0',
        gameVersionContentHash: 'b'.repeat(64),
        certificationNotice:
          'All displayed metrics originate from certified backend calculations.',
        rtpDecomposition: { totalRtp: 0.51, categories: [] },
        rtpValidation: {
          targetRtp: 96,
          actualRtp: 51,
          difference: -45,
          tolerance: 0.1,
          withinTolerance: false,
        },
        rtpDecompositionChart: {
          BASE: 5,
          FREE_SPINS: 46,
          HOLD_AND_WIN: 0,
          JACKPOT: 0,
          totalRtp: 51,
        },
        featureValidation: [],
        recommendations: [],
      },
    },
    {
      simulationId: 'sim-2',
      runtimeDurationMs: 2200,
      detail: {
        id: 'sim-2',
        gameVersionId: 'version-1',
        status: 'completed',
        spinCount: 1000,
        completedSpinCount: 1000,
        betMinorUnits: 100,
        eventLogMode: 'none',
        createdAt: '2026-01-02T00:00:00Z',
        startedAt: '2026-01-02T00:00:01Z',
        completedAt: '2026-01-02T00:00:04Z',
        cancelRequested: false,
        workerId: 'worker-1',
        errorMessage: null,
        progress: { completedSpins: 1000, percentage: 100 },
      },
      results: {
        simulationId: 'sim-2',
        summary: { rtp: 0.961, uncappedRtp: 0.961, volatility: 3.5, hitFrequency: 0.25 },
        totals: { totalBetMinorUnits: 100000, totalWinMinorUnits: 96100 },
        featureFrequencies: [
          { featureName: 'FREE_SPINS', triggerCount: 350, frequency: 0.35, oneInX: 2.9 },
        ],
        jackpotFrequencies: [],
        exposure: {
          truncationRate: 0,
          totalTruncatedMinorUnits: 0,
          cappedRtp: 0.961,
          uncappedRtp: 0.961,
          rtpDifference: 0,
          exposureCapApplied: false,
        },
        confidenceInterval: {
          rtp: 0.961,
          lowerBound: 0.94,
          upperBound: 0.98,
          confidenceLevel: 0.95,
        },
        winDistribution: {
          totalSpins: 1000,
          betMinorUnitsPerSpin: 100,
          buckets: [{ label: '0x', count: 750, percentage: 75 }],
        },
        volatilityMetrics: {
          meanWinMinorUnits: 96.1,
          variance: 12.25,
          standardDeviation: 3.5,
          coefficientOfVariation: 0.036,
        },
        hitFrequency: {
          hitFrequency: 0.25,
          winningSpinCount: 250,
          losingSpinCount: 750,
        },
        engineVersion: 'runtime-core@1.8.0',
        gameVersionContentHash: 'b'.repeat(64),
        certificationNotice:
          'All displayed metrics originate from certified backend calculations.',
        rtpDecomposition: { totalRtp: 0.961, categories: [] },
        rtpValidation: {
          targetRtp: 96,
          actualRtp: 96.1,
          difference: 0.1,
          tolerance: 0.1,
          withinTolerance: true,
        },
        rtpDecompositionChart: {
          BASE: 20,
          FREE_SPINS: 76,
          HOLD_AND_WIN: 0,
          JACKPOT: 0,
          totalRtp: 96.1,
        },
        featureValidation: [],
        recommendations: [],
      },
    },
  ],
  comparison: {
    rtp: [
      { simulationId: 'sim-1', value: 0.51 },
      { simulationId: 'sim-2', value: 0.961 },
    ],
    volatility: [
      { simulationId: 'sim-1', value: 4 },
      { simulationId: 'sim-2', value: 3.5 },
    ],
    hitFrequency: [
      { simulationId: 'sim-1', value: 0.2 },
      { simulationId: 'sim-2', value: 0.25 },
    ],
    confidenceIntervals: [
      {
        simulationId: 'sim-1',
        lowerBound: 0.48,
        upperBound: 0.54,
        confidenceLevel: 0.95,
      },
      {
        simulationId: 'sim-2',
        lowerBound: 0.94,
        upperBound: 0.98,
        confidenceLevel: 0.95,
      },
    ],
    featureFrequency: [
      { simulationId: 'sim-1', featureName: 'FREE_SPINS', frequency: 0.684 },
      { simulationId: 'sim-2', featureName: 'FREE_SPINS', frequency: 0.35 },
    ],
    rtpDecomposition: [
      {
        simulationId: 'sim-1',
        BASE: 5,
        FREE_SPINS: 46,
        HOLD_AND_WIN: 0,
        JACKPOT: 0,
        totalRtp: 51,
      },
      {
        simulationId: 'sim-2',
        BASE: 20,
        FREE_SPINS: 76,
        HOLD_AND_WIN: 0,
        JACKPOT: 0,
        totalRtp: 96.1,
      },
    ],
  },
}

describe('workbench utilities', () => {
  it('extracts math configuration snapshot', () => {
    const snapshot = extractMathConfigSnapshot(canonicalJson)
    expect(snapshot.rtpTarget?.percent).toBe(96)
    expect(snapshot.scatterTriggers[0]?.emitTrigger).toBe('FREE_SPINS')
    expect(snapshot.paytableSummary[0]?.multiplier).toBe(100)
  })

  it('derives comparison highlights', () => {
    const highlights = deriveComparisonHighlights(compareData)
    expect(highlights.bestRtpMatchId).toBe('sim-2')
    expect(highlights.lowestVolatilityId).toBe('sim-2')
    expect(highlights.highestHitFrequencyId).toBe('sim-2')
  })

  it('formats runtime duration', () => {
    expect(formatDurationMs(1500)).toBe('1.5 s')
    expect(formatDurationMs(null)).toBe('—')
  })
})

describe('workbench components', () => {
  it('renders math configuration snapshot', async () => {
    const user = (await import('@testing-library/user-event')).default.setup()
    render(<MathConfigurationSnapshot canonicalJson={canonicalJson} />)
    expect(screen.getByText(/math configuration snapshot/i)).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: /math configuration snapshot/i }))
    expect(screen.getByText(/scatter triggers/i)).toBeInTheDocument()
    expect(screen.getByText('FREE_SPINS')).toBeInTheDocument()
  })

  it('renders comparison workbench', () => {
    render(<SimulationComparisonWorkbench data={compareData} />)
    expect(screen.getByText(/side-by-side metrics/i)).toBeInTheDocument()
    expect(screen.getByText(/rtp evolution/i)).toBeInTheDocument()
    expect(screen.getByText(/best rtp match/i)).toBeInTheDocument()
  })
})
