import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import {
  createMemoryHistory,
  createRouter,
  RouterProvider,
} from '@tanstack/react-router'
import { describe, expect, it, vi } from 'vitest'

import { router } from '@/app/router'
import { useAuthStore } from '@/stores/auth-store'
import { refreshTokenStorage } from '@/lib/refresh-token-storage'
import { authService } from '@/services/auth'

async function renderLoginRoute() {
  const memoryHistory = createMemoryHistory({ initialEntries: ['/login'] })
  const testRouter = createRouter({
    routeTree: router.routeTree,
    history: memoryHistory,
  })
  await testRouter.load()

  render(
    <QueryClientProvider client={new QueryClient()}>
      <RouterProvider router={testRouter} />
    </QueryClientProvider>,
  )

  return { testRouter, memoryHistory }
}

describe('LoginPage', () => {
  it('validates required fields', async () => {
    const user = userEvent.setup()
    await renderLoginRoute()

    await user.click(screen.getByRole('button', { name: /sign in/i }))

    expect(await screen.findByText(/invalid email/i)).toBeInTheDocument()
  })

  it('submits credentials', async () => {
    const user = userEvent.setup()
    const loginSpy = vi.spyOn(authService, 'login').mockResolvedValue({
      accessToken: 'access',
      refreshToken: 'refresh',
      tokenType: 'bearer',
      expiresIn: 900,
    })

    await renderLoginRoute()

    await user.type(screen.getByLabelText(/email/i), 'user@example.com')
    await user.type(screen.getByLabelText(/password/i), 'password123')
    await user.click(screen.getByRole('button', { name: /sign in/i }))

    await waitFor(() => {
      expect(loginSpy).toHaveBeenCalled()
    })
    expect(loginSpy.mock.calls[0]?.[0]).toEqual({
      email: 'user@example.com',
      password: 'password123',
    })
  })
})

describe('route protection', () => {
  it('redirects unauthenticated users away from dashboard', async () => {
    useAuthStore.getState().clear()
    refreshTokenStorage.clear()

    const history = createMemoryHistory({ initialEntries: ['/dashboard'] })
    const testRouter = createRouter({
      routeTree: router.routeTree,
      history,
    })
    await testRouter.load()

    render(
      <QueryClientProvider client={new QueryClient()}>
        <RouterProvider router={testRouter} />
      </QueryClientProvider>,
    )

    await waitFor(() => {
      expect(history.location.pathname).toBe('/login')
    })
  })
})

describe('auth store', () => {
  it('tracks access token in memory', () => {
    useAuthStore.getState().setAccessToken('token-123')
    expect(useAuthStore.getState().isAuthenticated()).toBe(true)
    useAuthStore.getState().clear()
    expect(useAuthStore.getState().isAuthenticated()).toBe(false)
  })
})

describe('refresh token storage', () => {
  it('stores and clears refresh tokens', () => {
    refreshTokenStorage.set('refresh-token')
    expect(refreshTokenStorage.get()).toBe('refresh-token')
    refreshTokenStorage.clear()
    expect(refreshTokenStorage.get()).toBeNull()
  })
})
