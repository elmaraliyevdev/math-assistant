import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, expect, it, vi } from 'vitest'

import { useGames } from '@/features/games/use-games'
import { useSimulations } from '@/features/simulations/use-simulations'
import { gamesService } from '@/services/games'
import { simulationsService } from '@/services/simulations'
import { useAuthStore } from '@/stores/auth-store'

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('useGames', () => {
  it('fetches games list', async () => {
    useAuthStore.getState().setAccessToken('token')
    vi.spyOn(gamesService, 'list').mockResolvedValue({
      items: [
        {
          id: 'game-1',
          organizationId: 'org-1',
          name: 'Test Game',
          description: null,
          createdAt: '2026-01-01T00:00:00Z',
          updatedAt: '2026-01-01T00:00:00Z',
        },
      ],
      total: 1,
      page: 1,
      pageSize: 20,
    })

    const { result } = renderHook(() => useGames(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data?.items[0]?.name).toBe('Test Game')
  })
})

describe('useSimulations', () => {
  it('fetches simulations list', async () => {
    vi.spyOn(simulationsService, 'list').mockResolvedValue({
      items: [
        {
          id: 'sim-1',
          gameVersionId: 'version-1',
          status: 'completed',
          spinCount: 1000,
          completedSpinCount: 1000,
          createdAt: '2026-01-01T00:00:00Z',
          completedAt: '2026-01-01T00:05:00Z',
          errorMessage: null,
        },
      ],
      total: 1,
      page: 1,
      pageSize: 20,
    })

    const { result } = renderHook(() => useSimulations(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data?.items[0]?.status).toBe('completed')
  })
})
