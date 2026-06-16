import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { SimulationForm } from '@/features/simulations/components/SimulationForm'

import { renderWithQuery } from './test-utils'

const games = [
  {
    id: 'game-1',
    organizationId: 'org-1',
    name: 'Lucky Stars',
    description: null,
    createdAt: '2026-01-01T00:00:00Z',
    updatedAt: '2026-01-01T00:00:00Z',
  },
]

describe('SimulationForm', () => {
  it('shows validation errors for empty submission', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()

    renderWithQuery(
      <SimulationForm
        games={games}
        submitLabel="Start"
        onSubmit={onSubmit}
      />,
    )

    await user.click(screen.getByRole('button', { name: /^start$/i }))
    expect(
      (await screen.findAllByText(/select a game/i)).length,
    ).toBeGreaterThan(0)
    expect(onSubmit).not.toHaveBeenCalled()
  })
})
