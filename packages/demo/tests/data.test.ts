import { describe, expect, it } from 'vitest'

import { demoCalibrateResponse, demoGame, demoSimulationResults } from '../src/data'

describe('demo data', () => {
  it('uses consistent Crown Quest identifiers', () => {
    expect(demoGame.name).toBe('Crown Quest')
    expect(demoSimulationResults.simulationId).toContain('crown-quest')
    expect(demoCalibrateResponse.calibration.withinTolerance).toBe(true)
  })

  it('uses Crown Quest v3.2 across demo entities', async () => {
    const { demoGameVersion } = await import('../src/data/games')
    expect(demoGameVersion.version).toBe(3.2)
  })

  it('keeps simulation RTP within certification tolerance', () => {
    expect(demoSimulationResults.rtpValidation.withinTolerance).toBe(true)
    expect(demoSimulationResults.summary.rtp).toBeGreaterThan(0.95)
  })
})
