import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, describe, expect, it } from 'vitest'

import { useGame, useGameVersions } from '@/features/games/use-games'
import { useCurrentOrganizationId, useOrganization } from '@/features/organizations/use-organizations'
import { useSimulation, useSimulationResults } from '@/features/simulations/use-simulations'
import { authService } from '@/services/auth'
import { gamesService } from '@/services/games'
import { refreshTokenStorage } from '@/lib/refresh-token-storage'
import { useAuthStore } from '@/stores/auth-store'
import { useOrganizationStore } from '@/stores/organization-store'

import './msw'

function wrapper({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider
      client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}
    >
      {children}
    </QueryClientProvider>
  )
}

describe('detail query hooks', () => {
  beforeEach(() => {
    useAuthStore.getState().setAccessToken('access-token')
  })

  it('loads a game and versions', async () => {
    const game = renderHook(() => useGame('game-1'), { wrapper })
    const versions = renderHook(() => useGameVersions('game-1'), { wrapper })

    await waitFor(() => expect(game.result.current.isSuccess).toBe(true))
    await waitFor(() => expect(versions.result.current.isSuccess).toBe(true))
    expect(game.result.current.data?.name).toBe('Lucky Stars')
    expect(versions.result.current.data?.[0]?.version).toBe(1)
  })

  it('loads simulation and organization detail', async () => {
    const simulation = renderHook(() => useSimulation('sim-1'), { wrapper })
    const organization = renderHook(() => useOrganization('org-1'), { wrapper })
    const results = renderHook(() => useSimulationResults('sim-1', true), { wrapper })
    const currentOrg = renderHook(() => useCurrentOrganizationId(), { wrapper })

    await waitFor(() => expect(simulation.result.current.isSuccess).toBe(true))
    await waitFor(() => expect(organization.result.current.isSuccess).toBe(true))
    expect(simulation.result.current.data?.status).toBe('running')
    expect(organization.result.current.data?.slug).toBe('workspace')
    expect(currentOrg.result.current.organizationId).toBeDefined()
    await waitFor(() => expect(results.result.current.isSuccess).toBe(true))
  })
})

describe('auth service edge cases', () => {
  it('returns null when refresh token missing', async () => {
    refreshTokenStorage.clear()
    const tokens = await authService.refresh()
    expect(tokens).toBeNull()
  })

  it('logs out through service', async () => {
    useAuthStore.getState().setAccessToken('access-token')
    refreshTokenStorage.set('refresh-token')
    await authService.logout()
    expect(useAuthStore.getState().accessToken).toBeNull()
  })
})

describe('organization store clear', () => {
  it('clears persisted organization', () => {
    useOrganizationStore.getState().setCurrentOrganizationId('org-1')
    useOrganizationStore.getState().clear()
    expect(useOrganizationStore.getState().currentOrganizationId).toBeNull()
  })
})

describe('games service detail', () => {
  it('loads a single game version', async () => {
    useAuthStore.getState().setAccessToken('access-token')
    const version = await gamesService.getVersion('game-1', 'version-1')
    expect(version.version).toBe(1)
    expect(version.canonicalJson).toEqual({ schemaVersion: '1.0.0' })
  })
})
