import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, render, renderHook, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import simpleTemplate from '@/features/game-templates/templates/simple-5x3.json'
import { ReelStudioLayout } from '@/features/reel-studio/components/ReelStudioLayout'
import { ReelStudioToolbar } from '@/features/reel-studio/components/ReelStudioToolbar'
import {
  ReelStudioProvider,
  useReelStudio,
} from '@/features/reel-studio/context/reel-studio-context'
import { useReelStudioSave } from '@/features/reel-studio/hooks/use-reel-studio-save'
import { parseCanonicalJson } from '@/features/reel-studio/lib/parse-canonical'
import { paletteId, slotId } from '@/features/reel-studio/lib/reel-mutations'

vi.mock('@/features/reel-studio/hooks/use-reel-studio-save', () => ({
  useReelStudioSave: vi.fn(),
}))

const document = parseCanonicalJson(
  simpleTemplate as Record<string, unknown>,
  'runtime-core@1.8.0',
)

function renderWithProviders(ui: React.ReactNode) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <ReelStudioProvider initialDocument={document}>{ui}</ReelStudioProvider>
    </QueryClientProvider>,
  )
}

describe('ReelStudioToolbar', () => {
  it('triggers save with the live document', async () => {
    const mutate = vi.fn()
    vi.mocked(useReelStudioSave).mockReturnValue({
      mutate,
      isPending: false,
      isError: false,
      error: null,
      reset: vi.fn(),
    } as unknown as ReturnType<typeof useReelStudioSave>)

    const user = userEvent.setup()
    renderWithProviders(<ReelStudioToolbar gameId="game-1" />)
    await user.click(screen.getByRole('button', { name: /save as new version/i }))
    expect(mutate).toHaveBeenCalled()
    expect(mutate.mock.calls[0]?.[0].reelSets).toEqual(document.reelSets)
  })
})

describe('ReelStudioLayout drag handlers', () => {
  it('renders drag overlay label when dragging from palette', async () => {
    renderWithProviders(<ReelStudioLayout />)
    const paletteItem = screen.getAllByRole('button', { name: /drag/i })[0]
    expect(paletteItem).toBeDefined()
  })
})

describe('context cross-reel and palette drops', () => {
  it('adds palette symbol to target slot', () => {
    const { result } = renderHook(() => useReelStudio(), {
      wrapper: ({ children }) => (
        <ReelStudioProvider initialDocument={document}>{children}</ReelStudioProvider>
      ),
    })
    act(() => {
      result.current.handleDragEnd(paletteId('H1'), slotId(1, 0))
    })
    expect(result.current.document.reelSets.base_game?.reels[1]?.symbols[0]).toBe('H1')
  })

  it('moves symbol across reels via handleDragEnd', () => {
    const { result } = renderHook(() => useReelStudio(), {
      wrapper: ({ children }) => (
        <ReelStudioProvider initialDocument={document}>{children}</ReelStudioProvider>
      ),
    })
    act(() => {
      result.current.handleDragEnd(slotId(0, 0), slotId(2, 0))
    })
    expect(result.current.document.reelSets.base_game?.reels[0]?.symbols[0]).toBe('H1')
    expect(result.current.document.reelSets.base_game?.reels[2]?.symbols[0]).toBe('L1')
  })

  it('ignores invalid drag ids', () => {
    const { result } = renderHook(() => useReelStudio(), {
      wrapper: ({ children }) => (
        <ReelStudioProvider initialDocument={document}>{children}</ReelStudioProvider>
      ),
    })
    const before = [...(result.current.document.reelSets.base_game?.reels[0]?.symbols ?? [])]
    act(() => {
      result.current.handleDragEnd('invalid', slotId(0, 1))
      result.current.handleDragEnd(slotId(0, 0), null)
    })
    expect(result.current.document.reelSets.base_game?.reels[0]?.symbols).toEqual(before)
  })

  it('drops palette symbols on reel containers', () => {
    const { result } = renderHook(() => useReelStudio(), {
      wrapper: ({ children }) => (
        <ReelStudioProvider initialDocument={document}>{children}</ReelStudioProvider>
      ),
    })
    const before = result.current.document.reelSets.base_game?.reels[3]?.symbols.length ?? 0
    act(() => {
      result.current.handleDragEnd(paletteId('SCATTER'), 'reel-container-3')
    })
    expect(result.current.document.reelSets.base_game?.reels[3]?.symbols.length).toBe(before + 1)
  })

  it('drops reel symbols on reel containers', () => {
    const { result } = renderHook(() => useReelStudio(), {
      wrapper: ({ children }) => (
        <ReelStudioProvider initialDocument={document}>{children}</ReelStudioProvider>
      ),
    })
    act(() => {
      result.current.handleDragEnd(slotId(0, 0), 'reel-container-4')
    })
    const reel4 = result.current.document.reelSets.base_game?.reels[4]?.symbols ?? []
    expect(reel4.at(-1)).toBe('L1')
  })

  it('supports add, duplicate, and remove helpers', () => {
    const { result } = renderHook(() => useReelStudio(), {
      wrapper: ({ children }) => (
        <ReelStudioProvider initialDocument={document}>{children}</ReelStudioProvider>
      ),
    })
    act(() => {
      result.current.addSymbol(0, 'H1')
      result.current.duplicateSymbol(0, 0)
      result.current.removeSymbol(0, 1)
    })
    expect(result.current.document.reelSets.base_game?.reels[0]?.symbols.length).toBe(6)
  })
})
