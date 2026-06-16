import './msw'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { renderHook, waitFor } from '@testing-library/react'
import type { ReactNode } from 'react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import {
  isSimulationActive,
  useCancelSimulation,
  useCreateSimulation,
  useSimulation,
  useSimulationResults,
  useSimulations,
} from '@/features/simulations/hooks/use-simulations'
import { simulationsApi } from '@/features/simulations/api/simulations-api'
import { useAuthStore } from '@/stores/auth-store'

vi.mock('@tanstack/react-router', () => ({
  useNavigate: () => vi.fn(),
}))

function wrapper({ children }: { children: ReactNode }) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('simulation hooks', () => {
  beforeEach(() => {
    useAuthStore.getState().setAccessToken('access-token')
  })

  it('identifies active simulation statuses', () => {
    expect(isSimulationActive('pending')).toBe(true)
    expect(isSimulationActive('running')).toBe(true)
    expect(isSimulationActive('completed')).toBe(false)
  })

  it('loads simulations list', async () => {
    const hook = renderHook(() => useSimulations({ page: 1 }), { wrapper })
    await waitFor(() => expect(hook.result.current.isSuccess).toBe(true))
    expect(hook.result.current.data?.items.length).toBeGreaterThan(0)
  })

  it('loads simulation detail with polling enabled', async () => {
    const hook = renderHook(() => useSimulation('sim-1', true), { wrapper })
    await waitFor(() => expect(hook.result.current.isSuccess).toBe(true))
    expect(hook.result.current.data?.status).toBe('running')
  })

  it('loads simulation results', async () => {
    const hook = renderHook(() => useSimulationResults('sim-1'), { wrapper })
    await waitFor(() => expect(hook.result.current.isSuccess).toBe(true))
    expect(hook.result.current.data?.summary.rtp).toBe(0.96)
  })

  it('cancels a simulation', async () => {
    const cancelSpy = vi.spyOn(simulationsApi, 'cancel')
    const hook = renderHook(() => useCancelSimulation('sim-1'), { wrapper })
    hook.result.current.mutate()
    await waitFor(() => expect(hook.result.current.isSuccess).toBe(true))
    expect(cancelSpy).toHaveBeenCalledWith('sim-1')
  })

  it('creates a simulation', async () => {
    const createSpy = vi.spyOn(simulationsApi, 'create')
    const hook = renderHook(() => useCreateSimulation(), { wrapper })
    hook.result.current.mutate({
      gameVersionId: 'version-1',
      spinCount: 100,
      betMinorUnits: 100,
    })
    await waitFor(() => expect(hook.result.current.isSuccess).toBe(true))
    expect(createSpy).toHaveBeenCalled()
  })
})
