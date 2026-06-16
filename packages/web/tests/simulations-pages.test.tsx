import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import { expectHeading, renderAt } from './test-utils'

describe('simulations list page', () => {
  it('renders filters and refresh control', async () => {
    await renderAt('/simulations')
    expect(screen.getByLabelText(/search/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/status/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /refresh/i })).toBeInTheDocument()
  })

  it('refreshes simulations list', async () => {
    const user = userEvent.setup()
    await renderAt('/simulations')
    await user.click(screen.getByRole('button', { name: /refresh/i }))
    expect(await screen.findByRole('button', { name: /refresh/i })).toBeEnabled()
  })

  it('filters simulations by search query', async () => {
    const user = userEvent.setup()
    await renderAt('/simulations')
    await screen.findAllByText(/lucky stars/i)

    await user.type(screen.getByLabelText(/search/i), 'sim-pending')

    await waitFor(() => {
      expect(screen.queryByText(/^pending$/i)).toBeInTheDocument()
    })
  })

  it('opens cancel confirmation from list', async () => {
    const user = userEvent.setup()
    await renderAt('/simulations')
    await screen.findAllByText(/lucky stars/i)

    const cancelButtons = await screen.findAllByRole('button', {
      name: /cancel/i,
    })
    await user.click(cancelButtons[0]!)

    expect(
      await screen.findByRole('heading', { name: /cancel simulation/i }),
    ).toBeInTheDocument()
  })

  it('navigates to next page', async () => {
    const user = userEvent.setup()
    await renderAt('/simulations')
    expect(await screen.findByText(/page 1 of/i)).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /next/i }))
    expect(await screen.findByText(/page 2 of/i)).toBeInTheDocument()
  })

  it('confirms simulation cancel from list', async () => {
    const user = userEvent.setup()
    await renderAt('/simulations')
    await screen.findAllByText(/lucky stars/i)

    const cancelButtons = await screen.findAllByRole('button', {
      name: /cancel/i,
    })
    await user.click(cancelButtons[0]!)

    await user.click(
      await screen.findByRole('button', { name: /^cancel simulation$/i }),
    )

    await waitFor(() => {
      expect(
        screen.queryByRole('heading', { name: /cancel simulation/i }),
      ).not.toBeInTheDocument()
    })
  })
})

describe('simulation detail page', () => {
  it('renders analytics dashboard for completed simulation', async () => {
    await renderAt('/simulations/sim-completed')
    await expectHeading(/simulation/i)
    expect(await screen.findByText(/rtp metrics/i)).toBeInTheDocument()
    expect(screen.getByText(/hit metrics/i)).toBeInTheDocument()
    expect(screen.getByText(/exposure metrics/i)).toBeInTheDocument()
    expect(screen.getByText(/win distribution/i)).toBeInTheDocument()
  })

  it('refreshes simulation detail results', async () => {
    const user = userEvent.setup()
    await renderAt('/simulations/sim-completed')
    await screen.findByText(/rtp metrics/i)

    await user.click(screen.getByRole('button', { name: /refresh results/i }))
    expect(await screen.findByText(/rtp metrics/i)).toBeInTheDocument()
  })

  it('shows cancel action for running simulation', async () => {
    await renderAt('/simulations/sim-1')
    expect(
      await screen.findByRole('button', { name: /cancel simulation/i }),
    ).toBeInTheDocument()
  })
})

describe('simulation create page', () => {
  it('renders game and version selectors', async () => {
    await renderAt('/simulations/create')
    await expectHeading(/create simulation/i)
    expect(screen.getByLabelText(/^game$/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/game version/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/spin count/i)).toBeInTheDocument()
  })
})
