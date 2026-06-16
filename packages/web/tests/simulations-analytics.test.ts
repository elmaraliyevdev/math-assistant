import { describe, expect, it } from 'vitest'

import { certifiedSimulationResults } from './fixtures/certified-results'

describe('certified simulation results fixture', () => {
  it('includes backend-provided analytics fields', () => {
    expect(certifiedSimulationResults.winDistribution.buckets).toHaveLength(8)
    expect(certifiedSimulationResults.confidenceInterval.lowerBound).toBeLessThan(
      certifiedSimulationResults.confidenceInterval.rtp,
    )
    expect(certifiedSimulationResults.volatilityMetrics.standardDeviation).toBe(
      certifiedSimulationResults.summary.volatility,
    )
    expect(certifiedSimulationResults.hitFrequency.winningSpinCount).toBe(280)
    expect(certifiedSimulationResults.exposure.exposureCapApplied).toBe(true)
    expect(certifiedSimulationResults.certificationNotice).toMatch(/certified backend/)
  })
})
