import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { expectHeading, renderAt } from './test-utils'

describe('protected pages', () => {
  it('renders dashboard statistics', async () => {
    await renderAt('/dashboard')
    await expectHeading(/dashboard/i)
    expect(await screen.findByText(/total simulations/i)).toBeInTheDocument()
    expect(await screen.findByText(/simulation completed/i)).toBeInTheDocument()
  })

  it('renders games list', async () => {
    await renderAt('/games')
    await expectHeading(/games/i)
    expect(await screen.findByText(/lucky stars/i)).toBeInTheDocument()
  })

  it('renders game detail', async () => {
    await renderAt('/games/game-1')
    await expectHeading(/lucky stars/i)
    expect(await screen.findByText(/version history/i)).toBeInTheDocument()
    expect(await screen.findByText(/v1/i)).toBeInTheDocument()
    expect(
      await screen.findByRole('button', { name: /^upload version$/i }),
    ).toBeInTheDocument()
  })

  it('renders templates page', async () => {
    await renderAt('/templates')
    await expectHeading(/templates/i)
    expect(await screen.findByText(/simple 5×3 slot/i)).toBeInTheDocument()
  })

  it('renders simulations list', async () => {
    await renderAt('/simulations')
    await expectHeading(/simulations/i)
    expect((await screen.findAllByText(/lucky stars/i)).length).toBeGreaterThan(0)
  })

  it('renders simulation detail with progress', async () => {
    await renderAt('/simulations/sim-1')
    await expectHeading(/simulation/i)
    expect(await screen.findByText(/25.0%/i)).toBeInTheDocument()
  })

  it('renders organization settings via settings team section', async () => {
    await renderAt('/settings?section=team')
    expect(await screen.findByText(/manage members, roles, and pending invitations/i)).toBeInTheDocument()
  })

  it('renders audit log via settings audit section', async () => {
    await renderAt('/settings?section=audit')
    await expectHeading(/audit log/i)
    expect(await screen.findByText(/test user/i)).toBeInTheDocument()
  })

  it('redirects legacy audit route to settings', async () => {
    await renderAt('/audit')
    await expectHeading(/audit log/i)
  })

  it('renders settings page', async () => {
    await renderAt('/settings')
    await expectHeading(/settings/i)
    expect(await screen.findByLabelText(/full name/i)).toBeInTheDocument()
  })
})

describe('game create page', () => {
  it('renders create form', async () => {
    await renderAt('/games/create')
    await expectHeading(/create game/i)
  })
})

describe('simulation create page', () => {
  it('renders create form', async () => {
    await renderAt('/simulations/create')
    await expectHeading(/create simulation/i)
  })
})

describe('games list pagination', () => {
  it('renders pagination controls', async () => {
    await renderAt('/games')
    expect(await screen.findByText(/page 1 of/i)).toBeInTheDocument()
  })
})

describe('simulations list pagination', () => {
  it('renders pagination controls', async () => {
    await renderAt('/simulations')
    expect(await screen.findByText(/page 1 of/i)).toBeInTheDocument()
  })
})

describe('game version page', () => {
  it('renders version detail', async () => {
    await renderAt('/games/game-1/versions/version-1')
    expect(await screen.findByRole('heading', { name: /version 1/i })).toBeInTheDocument()
    expect(screen.getAllByText(/canonical json/i).length).toBeGreaterThan(0)
  })

  it('shows export json action', async () => {
    await renderAt('/games/game-1/versions/version-1')
    expect(await screen.findByRole('button', { name: /export json/i })).toBeInTheDocument()
  })
})

describe('completed simulation page', () => {
  it('shows export controls', async () => {
    await renderAt('/simulations/sim-completed')
    expect(await screen.findByRole('button', { name: /export/i })).toBeInTheDocument()
  })
})
