import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import simpleTemplate from '@/features/game-templates/templates/simple-5x3.json'
import { ReelEditor } from '@/features/reel-studio/components/ReelEditor'
import { ReelSetSelector } from '@/features/reel-studio/components/ReelSetSelector'
import { ReelStatisticsPanel } from '@/features/reel-studio/components/ReelStatisticsPanel'
import { ReelStudioLayout } from '@/features/reel-studio/components/ReelStudioLayout'
import { SymbolPalette } from '@/features/reel-studio/components/SymbolPalette'
import {
  ReelStudioProvider,
  useReelStudio,
} from '@/features/reel-studio/context/reel-studio-context'
import { StudioCanvasProvider } from '@/features/reel-studio/layout/studio-canvas-context'
import { parseCanonicalJson } from '@/features/reel-studio/lib/parse-canonical'
import { mergeReelSetsIntoCanonical } from '@/features/reel-studio/lib/serialize-canonical'

describe('Reel Studio components', () => {
  const document = parseCanonicalJson(
    simpleTemplate as Record<string, unknown>,
    'runtime-core@1.8.0',
  )

  it('renders symbol palette with ids and types', () => {
    render(<SymbolPalette symbols={document.symbols} />)
    expect(screen.getByText('H1')).toBeInTheDocument()
    expect(screen.getByText('scatter')).toBeInTheDocument()
  })

  it('loads reels and statistics from JSON', () => {
    render(
      <ReelStudioProvider initialDocument={document}>
        <ReelStatisticsPanel />
      </ReelStudioProvider>,
    )
    expect(screen.getByText(/live statistics/i)).toBeInTheDocument()
    expect(screen.getByText(/reel 1/i)).toBeInTheDocument()
    expect(screen.getByText(/totals/i)).toBeInTheDocument()
  })

  it('updates statistics after symbol removal', async () => {
    const user = userEvent.setup()
    let removeSymbol: ((reelIndex: number, symbolIndex: number) => void) | undefined

    render(
      <ReelStudioProvider initialDocument={document}>
        <ReelStatisticsPanel />
        <button
          type="button"
          onClick={() => removeSymbol?.(0, 0)}
        >
          Remove first symbol
        </button>
        <SymbolRemover onReady={(fn) => { removeSymbol = fn }} />
      </ReelStudioProvider>,
    )

    expect(screen.getAllByText(/5 symbols/i).length).toBeGreaterThan(0)
    await user.click(screen.getByRole('button', { name: /remove first symbol/i }))
    expect(screen.getAllByText(/4 symbols/i).length).toBeGreaterThan(0)
  })

  it('clicks duplicate and remove on reel symbols', async () => {
    const user = userEvent.setup()
    render(
      <ReelStudioProvider initialDocument={document}>
        <ReelStudioLayout />
      </ReelStudioProvider>,
    )
    const duplicateButtons = screen.getAllByRole('button', { name: /^duplicate/i })
    const removeButtons = screen.getAllByRole('button', { name: /^remove/i })
    await user.click(duplicateButtons[0]!)
    await user.click(removeButtons[0]!)
    expect(screen.getAllByText(/symbols/i).length).toBeGreaterThan(0)
  })

  it('closes JSON preview drawer', async () => {
    const user = userEvent.setup()
    render(
      <ReelStudioProvider initialDocument={document}>
        <ReelStudioLayout />
      </ReelStudioProvider>,
    )

    await user.click(screen.getByRole('button', { name: /json preview/i }))
    expect(screen.getByText(/canonical json preview/i)).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: /^close$/i }))
    expect(screen.queryByText(/canonical json preview/i)).not.toBeInTheDocument()
  })

  it('renders empty reel set message', () => {
    const emptyDocument = {
      ...document,
      reelSets: {},
      activeReelSetId: 'missing',
    }
    render(
      <ReelStudioProvider initialDocument={emptyDocument}>
        <StudioCanvasProvider>
          <ReelEditor />
        </StudioCanvasProvider>
      </ReelStudioProvider>,
    )
    expect(screen.getByText(/no reel set selected/i)).toBeInTheDocument()
  })

  it('shows JSON preview content', async () => {
    const user = userEvent.setup()
    render(
      <ReelStudioProvider initialDocument={document}>
        <ReelStudioLayout />
      </ReelStudioProvider>,
    )

    await user.click(screen.getByRole('button', { name: /json preview/i }))
    expect(screen.getByText(/reelSets/i)).toBeInTheDocument()
  })

  it('switches reel sets when multiple are present', async () => {
    const multiSetDocument = {
      ...document,
      reelSets: {
        ...document.reelSets,
        free_spins: {
          id: 'free_spins',
          reels: document.reelSets.base_game!.reels.map((reel) => ({
            ...reel,
            symbols: [...reel.symbols],
          })),
        },
      },
    }
    const user = userEvent.setup()
    render(
      <ReelStudioProvider initialDocument={multiSetDocument}>
        <ReelSetSelector />
      </ReelStudioProvider>,
    )

    await user.click(screen.getByRole('button', { name: 'free_spins' }))
    expect(screen.getByRole('button', { name: 'free_spins' })).toHaveClass('bg-primary')
  })

  it('serializes preview JSON from provider state', () => {
    let preview: Record<string, unknown> | undefined
    render(
      <ReelStudioProvider initialDocument={document}>
        <PreviewCapture onPreview={(value) => { preview = value }} />
      </ReelStudioProvider>,
    )
    expect(preview).toBeDefined()
    expect(preview?.reelSets).toBeDefined()
    expect(mergeReelSetsIntoCanonical(document.originalCanonicalJson, document.reelSets)).toEqual(
      preview,
    )
  })
})

function PreviewCapture({ onPreview }: { onPreview: (value: Record<string, unknown>) => void }) {
  const { previewJson } = useReelStudio()
  onPreview(previewJson)
  return null
}

function SymbolRemover({
  onReady,
}: {
  onReady: (remove: (reelIndex: number, symbolIndex: number) => void) => void
}) {
  const { removeSymbol } = useReelStudio()
  onReady(removeSymbol)
  return null
}
