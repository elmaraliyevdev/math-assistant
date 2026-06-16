import { beforeEach, describe, expect, it } from 'vitest'

import { buildComparisonDeltas } from '@/features/workbench/comparison-deltas'
import {
  deleteComparisonSession,
  listComparisonSessions,
  saveComparisonSession,
} from '@/features/workbench/comparison-sessions'
import {
  estimateRuntimeSeconds,
  formatEstimatedRuntime,
} from '@/features/workbench/runtime-estimate'
import {
  buildReviewPacketNote,
  listTuningDecisions,
  upsertTuningDecision,
} from '@/features/workbench/tuning-decisions'
import type { SimulationCompareResponse } from '@/types/api'
import { certifiedSimulationResults } from './fixtures/certified-results'

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
        summary: { ...certifiedSimulationResults.summary, rtp: 0.96, volatility: 4.0, hitFrequency: 0.3 },
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

describe('workbench runtime estimate', () => {
  it('formats short and long durations', () => {
    expect(formatEstimatedRuntime(45)).toBe('~45s')
    expect(formatEstimatedRuntime(125)).toBe('~2m 5s')
    expect(formatEstimatedRuntime(120)).toBe('~2m')
    expect(formatEstimatedRuntime(3660)).toBe('~1h 1m')
    expect(formatEstimatedRuntime(7200)).toBe('~2h')
  })

  it('estimates runtime from throughput', () => {
    expect(estimateRuntimeSeconds(100_000, 50_000)).toBe(2)
    expect(estimateRuntimeSeconds(0, 50_000)).toBe(0)
    expect(estimateRuntimeSeconds(100, 0)).toBe(0)
  })
})

describe('comparison deltas', () => {
  it('builds delta rows against baseline', () => {
    const rows = buildComparisonDeltas(compareData)
    expect(rows).toHaveLength(2)
    expect(rows[0].rtpDelta).toBeNull()
    expect(rows[1].rtpDelta).toBeCloseTo(-0.02)
    expect(rows[1].label).toContain('Lucky Stars')
  })

  it('returns empty rows when no simulations are present', () => {
    expect(
      buildComparisonDeltas({
        ...compareData,
        simulations: [],
      }),
    ).toEqual([])
  })

  it('falls back to run labels and feature frequency deltas', () => {
    const rows = buildComparisonDeltas({
      ...compareData,
      simulations: [
        {
          ...compareData.simulations[0],
          gameName: undefined,
          gameVersionLabel: undefined,
          results: {
            ...compareData.simulations[0].results,
            featureFrequencies: [{ featureName: 'Free Spins', triggerCount: 1, frequency: 0.02, oneInX: 50 }],
          },
        },
        {
          ...compareData.simulations[1],
          simulationId: 'sim-3',
          gameName: undefined,
          gameVersionLabel: undefined,
          results: {
            ...compareData.simulations[1].results,
            featureFrequencies: [{ featureName: 'Free Spins', triggerCount: 2, frequency: 0.04, oneInX: 25 }],
          },
        },
      ],
    })
    expect(rows[0].label).toBe('Run 1')
    expect(rows[1].featureFrequencyDelta).toBeCloseTo(0.02)
  })
})

describe('comparison sessions', () => {
  beforeEach(() => {
    window.localStorage.clear()
  })

  it('saves and deletes named sessions', () => {
    saveComparisonSession({
      name: 'Certification A/B',
      simulationIds: ['sim-1', 'sim-2'],
    })
    expect(listComparisonSessions()).toHaveLength(1)
    deleteComparisonSession(listComparisonSessions()[0].id)
    expect(listComparisonSessions()).toHaveLength(0)
  })

  it('updates an existing session by id', () => {
    const saved = saveComparisonSession({
      id: 'session-1',
      name: 'Draft',
      simulationIds: ['sim-1'],
    })
    saveComparisonSession({
      id: saved.id,
      name: 'Final',
      simulationIds: ['sim-1', 'sim-2'],
    })
    expect(listComparisonSessions()[0].name).toBe('Final')
  })

  it('ignores invalid stored sessions', () => {
    window.localStorage.setItem('math-assistant-comparison-sessions', '{bad json')
    expect(listComparisonSessions()).toEqual([])
  })
})

describe('tuning decisions', () => {
  beforeEach(() => {
    window.localStorage.clear()
  })

  it('tracks accepted and rejected recommendations', () => {
    upsertTuningDecision('sim-1', {
      recommendationKey: 'reduce-scatter',
      title: 'Reduce SCATTER frequency',
      description: 'Lower trigger rate',
      status: 'accepted',
      note: 'Will update reel weights',
    })
    const decisions = listTuningDecisions('sim-1')
    expect(decisions[0].status).toBe('accepted')
    expect(buildReviewPacketNote(decisions)).toContain('Reduce SCATTER frequency')
  })

  it('ignores invalid stored decisions and omits empty notes', () => {
    window.localStorage.setItem(
      'math-assistant-tuning-decisions:sim-2',
      '{bad json',
    )
    expect(listTuningDecisions('sim-2')).toEqual([])
    expect(
      buildReviewPacketNote([
        {
          recommendationKey: 'a',
          title: 'Adjust H1 payout',
          description: 'Increase multiplier',
          status: 'rejected',
          note: '',
          updatedAt: '2026-01-01T00:00:00Z',
        },
      ]),
    ).toBe('Tuning review packet:\n- [REJECTED] Adjust H1 payout')
  })
})
