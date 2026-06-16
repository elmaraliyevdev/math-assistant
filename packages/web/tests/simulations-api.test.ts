import { describe, expect, it } from 'vitest'

import { simulationsApi } from '@/features/simulations/api/simulations-api'

import './msw'

describe('simulationsApi', () => {
  it('lists simulations with pagination params', async () => {
    const list = await simulationsApi.list({ page: 1, pageSize: 10 })
    expect(list.items.length).toBeGreaterThan(0)
    expect(list.page).toBe(1)
  })

  it('gets simulation detail and results', async () => {
    const detail = await simulationsApi.get('sim-1')
    expect(detail.status).toBe('running')

    const results = await simulationsApi.getResults('sim-1')
    expect(results.summary.rtp).toBe(0.96)
  })
})
