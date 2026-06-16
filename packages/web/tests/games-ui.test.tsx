import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, expect, it, vi } from 'vitest'

import { GameForm } from '@/features/games/components/GameForm'
import { VersionUploadDialog } from '@/features/games/components/VersionUploadDialog'

function renderWithQuery(ui: React.ReactNode) {
  return render(
    <QueryClientProvider client={new QueryClient()}>{ui}</QueryClientProvider>,
  )
}

describe('GameForm', () => {
  it('shows validation error when name is missing', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()

    render(<GameForm submitLabel="Save" onSubmit={onSubmit} />)
    await user.click(screen.getByRole('button', { name: /save/i }))
    expect(screen.getByText(/name is required/i)).toBeInTheDocument()
    expect(onSubmit).not.toHaveBeenCalled()
  })
})

describe('VersionUploadDialog', () => {
  it('renders upload form when open', () => {
    renderWithQuery(
      <VersionUploadDialog gameId="game-1" open onOpenChange={() => undefined} />,
    )
    expect(screen.getByText(/upload game version/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /paste json/i })).toBeInTheDocument()
  })
})
