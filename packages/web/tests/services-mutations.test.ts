import { beforeEach, describe, expect, it } from 'vitest'

import { authService } from '@/services/auth'
import { gamesService } from '@/services/games'
import { organizationsService } from '@/services/organizations'
import { simulationsService } from '@/services/simulations'
import { refreshTokenStorage } from '@/lib/refresh-token-storage'
import { useAuthStore } from '@/stores/auth-store'

import './msw'

describe('service mutations', () => {
  beforeEach(() => {
    useAuthStore.getState().setAccessToken('access-token')
    refreshTokenStorage.set('refresh-token')
  })

  it('logs out and clears session', async () => {
    await authService.logout()
    expect(useAuthStore.getState().accessToken).toBeNull()
    expect(refreshTokenStorage.get()).toBeNull()
  })

  it('creates and updates games', async () => {
    const created = await gamesService.create({
      name: 'New Game',
      organizationId: 'org-1',
    })
    expect(created.id).toBe('game-2')

    const updated = await gamesService.update('game-1', { name: 'Updated Game' })
    expect(updated.name).toBe('Updated Game')

    await gamesService.remove('game-1')
  })

  it('creates game versions', async () => {
    const version = await gamesService.createVersion('game-1', {
      canonicalJson: { schemaVersion: '1.0.0' },
      engineVersion: 'runtime-core@1.8.0',
    })
    expect(version.version).toBe(2)
  })

  it('creates and cancels simulations', async () => {
    const created = await simulationsService.create({
      gameVersionId: 'version-1',
      spinCount: 500,
    })
    expect(created.simulationId).toBe('sim-2')

    const cancelled = await simulationsService.cancel('sim-1')
    expect(cancelled.cancelRequested).toBe(true)
  })

  it('manages organizations', async () => {
    const created = await organizationsService.create({
      name: 'Studio',
      slug: 'studio',
    })
    expect(created.slug).toBe('studio')

    const updated = await organizationsService.update('org-1', {
      name: 'Updated Workspace',
    })
    expect(updated.name).toBe('Updated Workspace')

    const member = await organizationsService.addMember('org-1', {
      userId: 'user-2',
      role: 'developer',
    })
    expect(member.role).toBe('developer')

    await organizationsService.removeMember('org-1', 'user-2')
  })
})
