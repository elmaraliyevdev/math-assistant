import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { ValidationFindingsTable } from '@/features/games/components/ValidationFindingsTable'
import { JsonViewer } from '@/features/games/components/JsonViewer'
import { GameTableEmpty } from '@/features/games/components/GameTable'

describe('ValidationFindingsTable', () => {
  it('renders findings rows', () => {
    render(
      <ValidationFindingsTable
        findings={[
          {
            code: 'MISSING_FIELD',
            severity: 'error',
            message: 'Field required',
            path: '/metadata/title',
          },
        ]}
      />,
    )
    expect(screen.getByText('MISSING_FIELD')).toBeInTheDocument()
    expect(screen.getByText('Field required')).toBeInTheDocument()
  })

  it('shows empty message when no findings', () => {
    render(<ValidationFindingsTable findings={[]} emptyMessage="All clear" />)
    expect(screen.getByText('All clear')).toBeInTheDocument()
  })
})

describe('JsonViewer', () => {
  it('renders collapsible JSON', () => {
    render(<JsonViewer value={{ schemaVersion: '1.0.0', reels: [1, 2] }} />)
    expect(screen.getByText(/Canonical JSON/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /copy/i })).toBeInTheDocument()
  })
})

describe('GameTableEmpty', () => {
  it('shows search-specific empty state', () => {
    render(<GameTableEmpty hasSearch />)
    expect(screen.getByText(/no games match your search/i)).toBeInTheDocument()
  })
})
