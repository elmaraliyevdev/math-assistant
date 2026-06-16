import { describe, expect, it } from 'vitest'

import { simulationFormSchema } from '@/features/simulations/schemas/simulation-schemas'

describe('simulationFormSchema', () => {
  it('accepts valid simulation input', () => {
    const parsed = simulationFormSchema.safeParse({
      gameId: 'game-1',
      gameVersionId: '660e8400-e29b-41d4-a716-446655440001',
      spinCount: 1000,
      betMinorUnits: 100,
      eventLogMode: 'none',
    })
    expect(parsed.success).toBe(true)
  })

  it('rejects missing game selection', () => {
    const parsed = simulationFormSchema.safeParse({
      gameId: '',
      gameVersionId: '660e8400-e29b-41d4-a716-446655440001',
      spinCount: 1000,
      betMinorUnits: 100,
      eventLogMode: 'none',
    })
    expect(parsed.success).toBe(false)
  })

  it('rejects invalid spin count', () => {
    const parsed = simulationFormSchema.safeParse({
      gameId: 'game-1',
      gameVersionId: '660e8400-e29b-41d4-a716-446655440001',
      spinCount: 0,
      betMinorUnits: 100,
      eventLogMode: 'none',
    })
    expect(parsed.success).toBe(false)
  })
})
