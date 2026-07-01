import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { EmptyState } from '@/components/empty-state'
import { GlossaryTerm } from '@/components/glossary-term'
import { MobileNav } from '@/components/mobile-nav'
import { GameTableEmpty } from '@/features/games/components/GameTable'
import { OnboardingProgressHeader } from '@/features/onboarding/components/OnboardingProgressHeader'
import {
  getEstimatedRemainingMinutes,
  getOnboardingProgress,
} from '@/features/onboarding/progress'
import { SimulationTableEmpty } from '@/features/simulations/components/SimulationTable'
import { GLOSSARY, getGlossaryDefinition } from '@/lib/glossary'
import { NAV_ITEMS } from '@/lib/navigation'

const logoutMutate = vi.fn()

vi.mock('@tanstack/react-router', () => ({
  Link: ({
    children,
    to,
    onClick,
  }: {
    children: React.ReactNode
    to: string
    onClick?: () => void
  }) => (
    <a href={to} onClick={onClick}>
      {children}
    </a>
  ),
  useNavigate: () => vi.fn(),
}))

vi.mock('@/features/auth/use-auth', () => ({
  useLogout: () => ({ mutate: logoutMutate }),
}))

describe('platform polish components', () => {
  it('renders empty state with actions', () => {
    render(
      <EmptyState
        title="No items"
        description="Create one to begin."
        actions={<button type="button">Create</button>}
      />,
    )

    expect(screen.getByText('No items')).toBeInTheDocument()
    expect(screen.getByText('Create one to begin.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Create' })).toBeInTheDocument()
  })

  it('renders glossary term with help tooltip description', () => {
    render(<GlossaryTerm term="rtp" />)

    expect(screen.getByText('RTP')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Show help' })).toHaveAttribute(
      'title',
      GLOSSARY.rtp.definition,
    )
  })

  it('opens mobile navigation with all sidebar routes', async () => {
    const user = userEvent.setup()
    render(<MobileNav />)

    expect(screen.getByRole('button', { name: 'Open navigation menu' })).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Open navigation menu' }))

    for (const item of NAV_ITEMS) {
      expect(screen.getByRole('link', { name: item.label })).toHaveAttribute('href', item.to)
    }
  })

  it('closes mobile navigation when a route is selected', async () => {
    const user = userEvent.setup()
    render(<MobileNav />)

    await user.click(screen.getByRole('button', { name: 'Open navigation menu' }))
    await user.click(screen.getByRole('link', { name: 'Dashboard' }))

    expect(screen.queryByRole('link', { name: 'Settings' })).not.toBeInTheDocument()
  })

  it('signs out from mobile navigation', async () => {
    const user = userEvent.setup()
    render(<MobileNav />)

    await user.click(screen.getByRole('button', { name: 'Open navigation menu' }))
    await user.click(screen.getByRole('button', { name: /sign out/i }))

    expect(logoutMutate).toHaveBeenCalled()
  })

  it('shows game table empty state CTAs', () => {
    render(<GameTableEmpty hasSearch={false} />)

    expect(screen.getByText('No games yet')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Create game' })).toHaveAttribute(
      'href',
      '/games/create',
    )
    expect(screen.getByRole('link', { name: 'Browse templates' })).toHaveAttribute(
      'href',
      '/templates',
    )
  })

  it('hides game empty CTAs when searching', () => {
    render(<GameTableEmpty hasSearch />)

    expect(screen.getByText('No games match your search')).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'Create game' })).not.toBeInTheDocument()
  })

  it('shows simulation table empty state CTAs', () => {
    render(<SimulationTableEmpty hasFilters={false} />)

    expect(screen.getByRole('link', { name: 'New simulation' })).toHaveAttribute(
      'href',
      '/simulations/create',
    )
    expect(screen.getByRole('link', { name: 'View games' })).toHaveAttribute('href', '/games')
  })

  it('renders onboarding progress header', () => {
    render(<OnboardingProgressHeader step="simulation" />)

    expect(screen.getByText('Step 5 of 6')).toBeInTheDocument()
    expect(screen.getByText(/min remaining/i)).toBeInTheDocument()
    expect(screen.getByLabelText('Onboarding progress')).toBeInTheDocument()
    expect(screen.getByText('5. Simulation')).toBeInTheDocument()
  })
})

describe('onboarding progress helpers', () => {
  it('calculates progress percent', () => {
    expect(getOnboardingProgress('welcome')).toEqual({
      current: 1,
      total: 6,
      percent: 17,
    })
    expect(getOnboardingProgress('results')).toEqual({
      current: 6,
      total: 6,
      percent: 100,
    })
  })

  it('estimates remaining minutes from current step', () => {
    expect(getEstimatedRemainingMinutes('welcome')).toBe(12)
    expect(getEstimatedRemainingMinutes('results')).toBe(2)
  })
})

describe('glossary helpers', () => {
  it('returns definitions for all required terms', () => {
    const terms = [
      'rtp',
      'hitFrequency',
      'volatility',
      'confidenceInterval',
      'exposureCap',
      'minorUnits',
      'determinism',
    ] as const

    for (const term of terms) {
      expect(getGlossaryDefinition(term)).toBe(GLOSSARY[term].definition)
    }
  })
})
