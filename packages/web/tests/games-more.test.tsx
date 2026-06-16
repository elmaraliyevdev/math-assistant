import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { JsonViewer } from '@/features/games/components/JsonViewer'
import { ValidationFindingsTable } from '@/features/games/components/ValidationFindingsTable'
import { GameTable } from '@/features/games/components/GameTable'
import { VersionTable } from '@/features/games/components/VersionTable'
import { getValidationFindings, parseApiError } from '@/lib/api-error'

describe('JsonViewer interactions', () => {
  it('renders nested object keys', () => {
    render(
      <JsonViewer
        value={{
          schemaVersion: '1.0.0',
          metadata: { title: 'Lucky Stars' },
        }}
      />,
    )

    expect(screen.getByText(/schemaVersion/i)).toBeInTheDocument()
    expect(screen.getByText(/metadata/i)).toBeInTheDocument()
  })

  it('renders array values', () => {
    render(<JsonViewer value={{ reels: [1, 2, 3] }} />)
    expect(screen.getByText(/Array\(3\)/i)).toBeInTheDocument()
  })
})

describe('ValidationFindingsTable severities', () => {
  it('renders warning and info severities', () => {
    render(
      <ValidationFindingsTable
        findings={[
          {
            code: 'WARN',
            severity: 'warning',
            message: 'Careful',
            path: '/a',
          },
          {
            code: 'INFO',
            severity: 'info',
            message: 'Note',
            path: '/b',
          },
        ]}
      />,
    )
    expect(screen.getByText('WARN')).toBeInTheDocument()
    expect(screen.getByText('INFO')).toBeInTheDocument()
  })
})

describe('GameTable loading', () => {
  it('renders skeleton rows while loading', () => {
    const { container } = render(
      <GameTable rows={[]} loading onEdit={() => undefined} onDelete={() => undefined} />,
    )
    expect(container.querySelectorAll('.animate-pulse').length).toBeGreaterThan(0)
  })
})

describe('VersionTable', () => {
  it('shows empty state without versions', () => {
    render(
      <VersionTable gameId="game-1" versions={[]} onViewJson={() => undefined} />,
    )
    expect(screen.getByText(/no versions uploaded/i)).toBeInTheDocument()
  })

  it('renders loading skeletons', () => {
    const { container } = render(
      <VersionTable
        gameId="game-1"
        versions={[]}
        loading
        onViewJson={() => undefined}
      />,
    )
    expect(container.querySelectorAll('.animate-pulse').length).toBeGreaterThan(0)
  })
})

describe('parseApiError edge cases', () => {
  it('returns null for non-axios errors', () => {
    expect(parseApiError(new Error('boom'))).toBeNull()
    expect(getValidationFindings(new Error('boom'))).toEqual([])
  })
})
