import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, expect, it } from 'vitest'

import { GameEditDialog } from '@/features/games/components/GameEditDialog'
import type { Game } from '@/types/api'

const game: Game = {
  id: 'game-1',
  organizationId: 'org-1',
  name: 'Lucky Stars',
  description: 'Demo',
  createdAt: '2026-01-01T00:00:00Z',
  updatedAt: '2026-01-02T00:00:00Z',
}

describe('GameEditDialog', () => {
  it('renders edit form for a game', () => {
    render(
      <QueryClientProvider client={new QueryClient()}>
        <GameEditDialog game={game} open onOpenChange={() => undefined} />
      </QueryClientProvider>,
    )
    expect(screen.getByText(/edit game/i)).toBeInTheDocument()
    expect(screen.getByDisplayValue('Lucky Stars')).toBeInTheDocument()
  })
})
