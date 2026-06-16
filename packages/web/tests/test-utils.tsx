import './msw'

import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import {
  createMemoryHistory,
  createRouter,
  RouterProvider,
} from '@tanstack/react-router'
import type { ReactNode } from 'react'
import { expect } from 'vitest'

import { AppLayout } from '@/app/layout'
import { router } from '@/app/router'
import { useAuthStore } from '@/stores/auth-store'
import { refreshTokenStorage } from '@/lib/refresh-token-storage'
import { useOrganizationStore } from '@/stores/organization-store'

export async function renderAt(path: string) {
  useAuthStore.getState().setAccessToken('access-token')
  refreshTokenStorage.set('refresh-token')
  useOrganizationStore.getState().setCurrentOrganizationId('org-1')

  const history = createMemoryHistory({ initialEntries: [path] })
  const testRouter = createRouter({
    routeTree: router.routeTree,
    history,
  })
  await testRouter.load()

  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })

  render(
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={testRouter} />
    </QueryClientProvider>,
  )

  return { history, testRouter }
}

export function renderWithQuery(ui: ReactNode) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>,
  )
}

export async function expectHeading(text: RegExp | string) {
  expect(await screen.findByRole('heading', { name: text })).toBeInTheDocument()
}

export async function waitForHeading(text: RegExp | string) {
  await waitFor(() => {
    expect(screen.getByRole('heading', { name: text })).toBeInTheDocument()
  })
}

export { AppLayout }
