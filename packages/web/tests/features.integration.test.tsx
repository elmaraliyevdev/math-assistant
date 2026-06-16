import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, expect, it } from 'vitest'

import { useMe } from '@/features/auth/use-auth'
import { useOrganizations } from '@/features/organizations/use-organizations'
import { useSyncOrganization } from '@/hooks/use-sync-organization'
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

describe('useMe integration', () => {
  it('loads current user profile', async () => {
    useAuthStore.getState().setAccessToken('access-token')
    const { result } = renderHook(() => useMe(), { wrapper })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data?.user.email).toBe('user@example.com')
  })
})

describe('useOrganizations integration', () => {
  it('loads organizations', async () => {
    useAuthStore.getState().setAccessToken('access-token')
    const { result } = renderHook(() => useOrganizations(), { wrapper })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data?.items[0]?.slug).toBe('workspace')
  })
})

describe('useSyncOrganization', () => {
  it('selects first organization when unset', async () => {
    useAuthStore.getState().setAccessToken('access-token')
    useOrganizationStore.getState().clear()

    const { result: meResult } = renderHook(() => useMe(), { wrapper })
    await waitFor(() => expect(meResult.current.isSuccess).toBe(true))

    renderHook(() => useSyncOrganization(), { wrapper })

    await waitFor(() => {
      expect(useOrganizationStore.getState().currentOrganizationId).toBe('org-1')
    })
  })
})
