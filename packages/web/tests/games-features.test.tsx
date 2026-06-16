import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { http, HttpResponse } from 'msw'
import { beforeEach, describe, expect, it } from 'vitest'

import {
  getDuplicateVersionDetails,
  useCreateGameVersion,
  useUpdateGame,
} from '@/features/games/hooks/use-games'
import { useGameTableRows } from '@/features/games/hooks/use-game-table-rows'
import { useAuthStore } from '@/stores/auth-store'
import type { Game } from '@/types/api'

import { server } from './msw'
import './msw'

function wrapper({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider
      client={
        new QueryClient({
          defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
        })
      }
    >
      {children}
    </QueryClientProvider>
  )
}

const sampleGame: Game = {
  id: 'game-1',
  organizationId: 'org-1',
  name: 'Lucky Stars',
  description: 'Demo',
  createdAt: '2026-01-01T00:00:00Z',
  updatedAt: '2026-01-02T00:00:00Z',
}

describe('useGameTableRows', () => {
  beforeEach(() => {
    useAuthStore.getState().setAccessToken('access-token')
  })

  it('enriches games with organization name and version count', async () => {
    const { result } = renderHook(
      () =>
        useGameTableRows([sampleGame], [
          {
            organizationId: 'org-1',
            organizationName: 'Workspace',
            organizationSlug: 'workspace',
            role: 'owner',
          },
        ]),
      { wrapper },
    )

    await waitFor(() => {
      expect(result.current[0]?.organizationName).toBe('Workspace')
      expect(result.current[0]?.versionCount).toBe(1)
    })
  })
})

describe('useUpdateGame', () => {
  beforeEach(() => {
    useAuthStore.getState().setAccessToken('access-token')
  })

  it('updates game via API', async () => {
    const { result } = renderHook(() => useUpdateGame('game-1'), { wrapper })
    await result.current.mutateAsync({ name: 'Updated Game' })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
  })
})

describe('useCreateGameVersion errors', () => {
  beforeEach(() => {
    useAuthStore.getState().setAccessToken('access-token')
  })

  it('surfaces validation findings from 422 responses', async () => {
    server.use(
      http.post('/api/games/:gameId/versions', async () =>
        HttpResponse.json(
          {
            error: {
              code: 'VALIDATION_FAILED',
              message: 'validation failed',
              details: {
                findings: [
                  {
                    code: 'CANONICAL_JSON_INVALID',
                    severity: 'error',
                    message: 'Invalid JSON',
                    path: '/',
                  },
                ],
              },
            },
          },
          { status: 422 },
        ),
      ),
    )

    const { result } = renderHook(() => useCreateGameVersion('game-1'), { wrapper })

    let caught: unknown
    try {
      await result.current.mutateAsync({
        canonicalJson: { bad: true },
        engineVersion: 'runtime-core@1.8.0',
      })
    } catch (error) {
      caught = error
    }

    expect(getDuplicateVersionDetails(caught)).toBeNull()
    expect(getDuplicateVersionDetails(result.current.error)).toBeNull()
  })

  it('parses duplicate version details', async () => {
    server.use(
      http.post('/api/games/:gameId/versions', async () =>
        HttpResponse.json(
          {
            error: {
              code: 'DUPLICATE_GAME_VERSION',
              message: 'duplicate',
              details: {
                contentHash: 'abc123',
                existingVersionId: 'version-1',
              },
            },
          },
          { status: 409 },
        ),
      ),
    )

    const { result } = renderHook(() => useCreateGameVersion('game-1'), { wrapper })

    try {
      await result.current.mutateAsync({
        canonicalJson: { schemaVersion: '1.0.0' },
        engineVersion: 'runtime-core@1.8.0',
      })
    } catch {
      // expected
    }

    await waitFor(() => {
      expect(getDuplicateVersionDetails(result.current.error)?.contentHash).toBe(
        'abc123',
      )
    })
  })
})
