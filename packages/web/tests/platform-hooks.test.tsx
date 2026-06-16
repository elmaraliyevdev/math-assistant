import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import type { ReactNode } from 'react'
import { describe, expect, it } from 'vitest'

import { useAuditLogs } from '@/features/audit/hooks/use-audit'
import { useDashboardSummary } from '@/features/dashboard/hooks/use-dashboard'
import {
  useMarkAllNotificationsRead,
  useMarkNotificationRead,
  useNotifications,
} from '@/features/notifications/hooks/use-notifications'
import {
  useChangePassword,
  useUpdatePreferences,
  useUpdateProfile,
  useUserPreferences,
} from '@/features/settings/hooks/use-settings'

import './msw'

function wrapper({ children }: { children: ReactNode }) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('platform hooks', () => {
  it('loads notifications', async () => {
    const { result } = renderHook(() => useNotifications({ page: 1 }), { wrapper })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data?.items.length).toBeGreaterThan(0)
  })

  it('marks notification read', async () => {
    const { result } = renderHook(() => useMarkNotificationRead(), { wrapper })
    await expect(result.current.mutateAsync('notif-1')).resolves.toBeDefined()
  })

  it('marks all notifications read', async () => {
    const { result } = renderHook(() => useMarkAllNotificationsRead(), { wrapper })
    await expect(result.current.mutateAsync()).resolves.toBeDefined()
  })

  it('loads audit logs', async () => {
    const { result } = renderHook(() => useAuditLogs({ page: 1 }), { wrapper })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data?.items[0]?.action).toBe('auth.login')
  })

  it('loads user preferences', async () => {
    const { result } = renderHook(() => useUserPreferences(), { wrapper })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data?.theme).toBe('light')
  })

  it('updates preferences profile and password', async () => {
    const prefs = renderHook(() => useUpdatePreferences(), { wrapper })
    await expect(
      prefs.result.current.mutateAsync({ theme: 'dark' }),
    ).resolves.toBeDefined()

    const profile = renderHook(() => useUpdateProfile(), { wrapper })
    await expect(
      profile.result.current.mutateAsync({ fullName: 'Hook User' }),
    ).resolves.toBeDefined()

    const password = renderHook(() => useChangePassword(), { wrapper })
    await expect(
      password.result.current.mutateAsync({
        currentPassword: 'secure-password',
        newPassword: 'hook-secure-password',
      }),
    ).resolves.toBeDefined()
  })

  it('loads dashboard summary', async () => {
    const { result } = renderHook(() => useDashboardSummary(), { wrapper })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data?.totalSimulations).toBe(12)
  })
})
