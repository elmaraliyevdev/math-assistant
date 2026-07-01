import { act, renderHook } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import simpleTemplate from '@/features/game-templates/templates/simple-5x3.json'
import {
  ReelStudioProvider,
  useReelStudio,
  useReelStudioDocument,
  useReelStudioPreview,
} from '@/features/reel-studio/context/reel-studio-context'
import { parseCanonicalJson } from '@/features/reel-studio/lib/parse-canonical'
import { paletteId, slotId } from '@/features/reel-studio/lib/reel-mutations'
import type { ReactNode } from 'react'

function wrapper(document: ReturnType<typeof parseCanonicalJson>) {
  return function Wrapper({ children }: { children: ReactNode }) {
    return <ReelStudioProvider initialDocument={document}>{children}</ReelStudioProvider>
  }
}

describe('ReelStudio context drag and drop', () => {
  const document = parseCanonicalJson(
    simpleTemplate as Record<string, unknown>,
    'runtime-core@1.8.0',
  )

  it('moves symbols via handleDragEnd', () => {
    const { result } = renderHook(() => useReelStudio(), { wrapper: wrapper(document) })
    act(() => {
      result.current.handleDragEnd(slotId(0, 0), slotId(0, 2))
    })
    const symbols = result.current.document.reelSets.base_game?.reels[0]?.symbols ?? []
    expect(symbols.slice(0, 3)).toEqual(['H1', 'SCATTER', 'L1'])
    expect(result.current.stats.reels[0]?.length).toBe(5)
  })

  it('adds palette symbols to reels', () => {
    const { result } = renderHook(() => useReelStudio(), { wrapper: wrapper(document) })
    const before = result.current.document.reelSets.base_game?.reels[4]?.symbols.length ?? 0
    act(() => {
      result.current.handleDragEnd(paletteId('H1'), 'reel-container-4')
    })
    const after = result.current.document.reelSets.base_game?.reels[4]?.symbols.length ?? 0
    expect(after).toBe(before + 1)
    expect(result.current.previewJson.reelSets).toBeDefined()
  })

  it('throws when used outside provider', () => {
    expect(() => renderHook(() => useReelStudio())).toThrow(
      /must be used within ReelStudioProvider/i,
    )
  })

  it('exposes document and preview helpers', () => {
    const { result: documentResult } = renderHook(() => useReelStudioDocument(), {
      wrapper: ({ children }) => (
        <ReelStudioProvider initialDocument={document}>{children}</ReelStudioProvider>
      ),
    })
    const { result: previewResult } = renderHook(() => useReelStudioPreview(), {
      wrapper: ({ children }) => (
        <ReelStudioProvider initialDocument={document}>{children}</ReelStudioProvider>
      ),
    })
    expect(documentResult.current.activeReelSetId).toBe('base_game')
    expect(previewResult.current.schemaVersion).toBe('1.0.0')
  })

  it('computes empty stats for missing reel set', () => {
    const brokenDocument = { ...document, activeReelSetId: 'missing' }
    const { result } = renderHook(() => useReelStudio(), {
      wrapper: ({ children }) => (
        <ReelStudioProvider initialDocument={brokenDocument}>{children}</ReelStudioProvider>
      ),
    })
    expect(result.current.stats.totals.totalSymbols).toBe(0)
  })

  it('drops symbols on the same reel container', () => {
    const { result } = renderHook(() => useReelStudio(), { wrapper: wrapper(document) })
    act(() => {
      result.current.handleDragEnd(slotId(0, 0), 'reel-container-0')
    })
    const symbols = result.current.document.reelSets.base_game?.reels[0]?.symbols ?? []
    expect(symbols.at(-1)).toBe('L1')
  })

  it('updates preview JSON after edits', () => {
    const { result } = renderHook(() => useReelStudio(), { wrapper: wrapper(document) })
    const before = JSON.stringify(result.current.previewJson)
    act(() => {
      result.current.removeSymbol(0, 0)
    })
    expect(JSON.stringify(result.current.previewJson)).not.toBe(before)
  })
})
