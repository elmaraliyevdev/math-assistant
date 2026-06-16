import { beforeEach, describe, expect, it } from 'vitest'

import { authService } from '@/services/auth'
import { gamesService } from '@/services/games'
import { organizationsService } from '@/services/organizations'
import { simulationsService } from '@/services/simulations'
import { useAuthStore } from '@/stores/auth-store'

import './msw'

describe('service integration via MSW', () => {
  beforeEach(() => {
    useAuthStore.getState().setAccessToken('access-token')
  })

  it('logs in and stores tokens', async () => {
    const tokens = await authService.login({
      email: 'user@example.com',
      password: 'password123',
    })
    expect(tokens.accessToken).toBe('access-token')
    expect(useAuthStore.getState().accessToken).toBe('access-token')
  })

  it('registers a user', async () => {
    const result = await authService.register({
      email: 'new@example.com',
      password: 'password123',
      fullName: 'New User',
    })
    expect(result.organizationId).toBe('org-1')
  })

  it('loads games', async () => {
    const games = await gamesService.list()
    expect(games.items).toHaveLength(1)
  })

  it('loads game versions', async () => {
    const versions = await gamesService.listVersions('game-1')
    expect(versions[0]?.version).toBe(1)
  })

  it('loads simulations and details', async () => {
    const list = await simulationsService.list()
    expect(list.total).toBe(12)
    const detail = await simulationsService.get('sim-1')
    expect(detail.progress.percentage).toBe(25)
    const results = await simulationsService.getResults('sim-1')
    expect(results.summary.rtp).toBe(0.96)
  })

  it('loads organizations', async () => {
    const orgs = await organizationsService.list()
    expect(orgs.items[0]?.slug).toBe('workspace')
    const org = await organizationsService.get('org-1')
    expect(org.name).toBe('Workspace')
  })
})
