import { beforeEach, describe, expect, it } from 'vitest'

import { DEFAULT_ENGINE_VERSION } from '@/features/games/schemas/game-schemas'
import { gamesApi } from '@/features/games/api/games-api'
import { useAuthStore } from '@/stores/auth-store'

import './msw'

describe('gamesApi', () => {
  beforeEach(() => {
    useAuthStore.getState().setAccessToken('access-token')
  })

  it('lists and fetches games', async () => {
    const list = await gamesApi.list({ page: 1, pageSize: 10 })
    expect(list.items.length).toBeGreaterThan(0)
    const game = await gamesApi.get(list.items[0]!.id)
    expect(game.name).toBeTruthy()
  })

  it('creates a version with default engine', async () => {
    const version = await gamesApi.createVersion('game-1', {
      canonicalJson: { schemaVersion: '1.0.0' },
      engineVersion: DEFAULT_ENGINE_VERSION,
    })
    expect(version.validationSummary.passed).toBe(true)
  })
})
