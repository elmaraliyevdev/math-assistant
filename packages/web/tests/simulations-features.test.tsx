import './msw'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { renderHook, waitFor } from '@testing-library/react'
import type { ReactNode } from 'react'
import { describe, expect, it } from 'vitest'

import { useSimulationTableRows } from '@/features/simulations/hooks/use-simulation-table-rows'
import type { Game, SimulationSummary } from '@/types/api'

const simulations: SimulationSummary[] = [
  {
    id: 'sim-1',
    gameVersionId: 'version-1',
    status: 'completed',
    spinCount: 1000,
    completedSpinCount: 1000,
    createdAt: '2026-01-01T00:00:00Z',
    completedAt: '2026-01-01T00:10:00Z',
    errorMessage: null,
  },
]

const games: Game[] = [
  {
    id: 'game-1',
    organizationId: 'org-1',
    name: 'Lucky Stars',
    description: null,
    createdAt: '2026-01-01T00:00:00Z',
    updatedAt: '2026-01-01T00:00:00Z',
  },
]

function wrapper({ children }: { children: ReactNode }) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('useSimulationTableRows', () => {
  it('enriches simulations with game and results data', async () => {
    const hook = renderHook(
      () =>
        useSimulationTableRows(simulations, games, [
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
      expect(hook.result.current[0]?.gameName).toBe('Lucky Stars')
    })

    await waitFor(() => {
      expect(hook.result.current[0]?.rtp).toBe(0.96)
    })

    expect(hook.result.current[0]?.versionNumber).toBe(1)
    expect(hook.result.current[0]?.organizationName).toBe('Workspace')
  })
})
