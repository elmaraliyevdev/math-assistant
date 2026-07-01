import type { Game, GameListResponse, GameVersionSummary } from '@web/types/api'

import {
  DEMO_ENGINE_VERSION,
  DEMO_GAME_ID,
  DEMO_ORGANIZATION_ID,
  DEMO_VERSION_ID,
} from './constants'

export const demoGame: Game = {
  id: DEMO_GAME_ID,
  organizationId: DEMO_ORGANIZATION_ID,
  name: 'Crown Quest',
  description: '5×3 video slot with free spins and hold-and-win bonus.',
  createdAt: '2026-01-15T10:00:00Z',
  updatedAt: '2026-06-10T14:30:00Z',
}

export const demoGameList: GameListResponse = {
  items: [
    demoGame,
    {
      id: 'game-neon-fruits',
      organizationId: DEMO_ORGANIZATION_ID,
      name: 'Neon Fruits',
      description: 'Classic fruit machine with respin feature.',
      createdAt: '2026-02-01T09:00:00Z',
      updatedAt: '2026-05-28T11:15:00Z',
    },
    {
      id: 'game-viking-gold',
      organizationId: DEMO_ORGANIZATION_ID,
      name: 'Viking Gold',
      description: 'High-volatility megaways prototype.',
      createdAt: '2026-03-12T16:45:00Z',
      updatedAt: '2026-06-01T08:20:00Z',
    },
  ],
  total: 3,
  page: 1,
  pageSize: 20,
}

export const demoGameVersion: GameVersionSummary = {
  id: DEMO_VERSION_ID,
  version: 3.2,
  contentHash: 'c4a8f2e91b3d7c6e5a0f1d2b3c4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2',
  engineVersion: DEMO_ENGINE_VERSION,
  createdAt: '2026-06-10T14:30:00Z',
}

export const demoGameVersions: GameVersionSummary[] = [
  {
    id: 'version-crown-quest-v1',
    version: 1,
    contentHash: 'a1b2c3d4e5f6789012345678901234567890abcd1234567890abcd1234567890ab',
    engineVersion: DEMO_ENGINE_VERSION,
    createdAt: '2026-01-15T10:00:00Z',
  },
  {
    id: 'version-crown-quest-v2',
    version: 2,
    contentHash: 'b2c3d4e5f6789012345678901234567890abcd1234567890abcd1234567890abcd',
    engineVersion: DEMO_ENGINE_VERSION,
    createdAt: '2026-04-02T09:15:00Z',
  },
  demoGameVersion,
]
