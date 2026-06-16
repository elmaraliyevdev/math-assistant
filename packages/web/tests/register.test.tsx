import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import {
  createMemoryHistory,
  createRouter,
  RouterProvider,
} from '@tanstack/react-router'
import { describe, expect, it } from 'vitest'

import { router } from '@/app/router'

import './msw'

async function renderPublic(path: string) {
  const history = createMemoryHistory({ initialEntries: [path] })
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
}

describe('register page', () => {
  it('renders registration form', async () => {
    await renderPublic('/register')
    expect(await screen.findByRole('heading', { name: /create account/i })).toBeInTheDocument()
    expect(screen.getByLabelText(/full name/i)).toBeInTheDocument()
  })

  it('validates password length', async () => {
    const user = userEvent.setup()
    await renderPublic('/register')

    await user.type(screen.getByLabelText(/full name/i), 'Alice')
    await user.type(screen.getByLabelText(/email/i), 'alice@example.com')
    await user.type(screen.getByLabelText(/password/i), 'short')
    await user.click(screen.getByRole('button', { name: /create account/i }))

    expect(
      await screen.findByText(/password must be at least 8 characters/i),
    ).toBeInTheDocument()
  })
})

describe('index route', () => {
  it('redirects to login when logged out', async () => {
    const history = createMemoryHistory({ initialEntries: ['/'] })
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
