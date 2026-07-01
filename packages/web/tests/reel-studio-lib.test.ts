import simpleTemplate from '@/features/game-templates/templates/simple-5x3.json'
import {
  resolveDragEndIds,
  resolveDragOverlayLabel,
} from '@/features/reel-studio/lib/drag-events'
import {
  addSymbolToReel,
  duplicateSymbolOnReel,
  moveSymbolBetweenReels,
  moveSymbolWithinReel,
  parsePaletteId,
  parseReelContainerId,
  parseSlotId,
  paletteId,
  removeSymbolFromReel,
  reelContainerId,
  setActiveReelSetId,
  slotId,
} from '@/features/reel-studio/lib/reel-mutations'
import { parseCanonicalJson } from '@/features/reel-studio/lib/parse-canonical'
import {
  mergeReelSetsIntoCanonical,
  serializeReelSets,
} from '@/features/reel-studio/lib/serialize-canonical'
import { computeReelSetStats } from '@/features/reel-studio/lib/statistics'
import { normalizeSymbolType, symbolTypeBadgeClass } from '@/features/reel-studio/lib/symbol-colors'
import { describe, expect, it } from 'vitest'

const canonicalJson = simpleTemplate as Record<string, unknown>

describe('parseCanonicalJson', () => {
  it('loads symbols and reel sets without losing data', () => {
    const document = parseCanonicalJson(canonicalJson, 'runtime-core@1.8.0')
    expect(document.activeReelSetId).toBe('base_game')
    expect(Object.keys(document.symbols)).toContain('H1')
    expect(document.reelSets.base_game?.reels).toHaveLength(5)
    expect(document.reelSets.base_game?.reels[0]?.symbols[0]).toBe('L1')
    expect(document.originalCanonicalJson).not.toBe(canonicalJson)
    expect(document.originalCanonicalJson.schemaVersion).toBe('1.0.0')
  })

  it('handles missing symbols and reel sets gracefully', () => {
    const document = parseCanonicalJson(
      { schemaVersion: '1.0.0', gameConfig: { defaultReelSetId: 'missing' } },
      'runtime-core@1.8.0',
    )
    expect(document.symbols).toEqual({})
    expect(document.activeReelSetId).toBe('base_game')
  })

  it('preserves optional weights on import', () => {
    const document = parseCanonicalJson(
      {
        reelSets: {
          base_game: {
            id: 'base_game',
            reels: [{ reelIndex: 0, symbols: ['A', 'B'], weights: [2, 1] }],
          },
        },
      },
      'runtime-core@1.8.0',
    )
    expect(document.reelSets.base_game?.reels[0]?.weights).toEqual([2, 1])
  })
})

describe('serialize and merge', () => {
  it('only changes reelSets while preserving key order', () => {
    const document = parseCanonicalJson(canonicalJson, 'runtime-core@1.8.0')
    const edited = addSymbolToReel(document, 0, 'H1', 0)
    const merged = mergeReelSetsIntoCanonical(
      document.originalCanonicalJson,
      edited.reelSets,
    )
    const originalKeys = Object.keys(document.originalCanonicalJson)
    expect(Object.keys(merged)).toEqual(originalKeys)
    expect(merged.metadata).toBe(document.originalCanonicalJson.metadata)
    expect(merged.symbols).toBe(document.originalCanonicalJson.symbols)
    const reelSets = merged.reelSets as Record<string, unknown>
    const baseGame = reelSets.base_game as { reels: Array<{ symbols: string[] }> }
    expect(baseGame.reels[0]?.symbols[0]).toBe('H1')
  })

  it('serializes reel sets to canonical structure', () => {
    const document = parseCanonicalJson(canonicalJson, 'runtime-core@1.8.0')
    const serialized = serializeReelSets(document.reelSets)
    expect(serialized.base_game).toMatchObject({ id: 'base_game' })
  })
})

describe('reel mutations', () => {
  it('moves symbols within a reel', () => {
    const document = parseCanonicalJson(canonicalJson, 'runtime-core@1.8.0')
    const updated = moveSymbolWithinReel(document, 0, 0, 2)
    const symbols = updated.reelSets.base_game?.reels[0]?.symbols ?? []
    expect(symbols.slice(0, 3)).toEqual(['H1', 'SCATTER', 'L1'])
  })

  it('moves symbols between reels', () => {
    const document = parseCanonicalJson(canonicalJson, 'runtime-core@1.8.0')
    const updated = moveSymbolBetweenReels(document, 0, 0, 1, 0)
    expect(updated.reelSets.base_game?.reels[0]?.symbols[0]).toBe('H1')
    expect(updated.reelSets.base_game?.reels[1]?.symbols[0]).toBe('L1')
  })

  it('syncs weights when moving within a weighted reel', () => {
    const document = parseCanonicalJson(
      {
        reelSets: {
          base_game: {
            id: 'base_game',
            reels: [{ reelIndex: 0, symbols: ['A', 'B', 'C'], weights: [1, 2, 3] }],
          },
        },
      },
      'runtime-core@1.8.0',
    )
    const updated = moveSymbolWithinReel(document, 0, 0, 2)
    expect(updated.reelSets.base_game?.reels[0]?.weights).toEqual([2, 3, 1])
  })

  it('adds, removes, and duplicates symbols', () => {
    let document = parseCanonicalJson(canonicalJson, 'runtime-core@1.8.0')
    document = addSymbolToReel(document, 2, 'SCATTER')
    expect(document.reelSets.base_game?.reels[2]?.symbols.at(-1)).toBe('SCATTER')
    document = duplicateSymbolOnReel(document, 2, 0)
    expect(document.reelSets.base_game?.reels[2]?.symbols[1]).toBe('L1')
    const length = document.reelSets.base_game?.reels[2]?.symbols.length ?? 0
    document = removeSymbolFromReel(document, 2, 0)
    expect(document.reelSets.base_game?.reels[2]?.symbols).toHaveLength(length - 1)
  })

  it('parses drag identifiers', () => {
    expect(parseSlotId(slotId(1, 2))).toEqual({ reelIndex: 1, symbolIndex: 2 })
    expect(parsePaletteId(paletteId('H1'))).toBe('H1')
    expect(parseReelContainerId(reelContainerId(3))).toBe(3)
  })

  it('switches active reel set', () => {
    const document = parseCanonicalJson(canonicalJson, 'runtime-core@1.8.0')
    const updated = setActiveReelSetId(document, 'base_game')
    expect(updated.activeReelSetId).toBe('base_game')
    const unchanged = setActiveReelSetId(document, 'missing')
    expect(unchanged.activeReelSetId).toBe(document.activeReelSetId)
  })
})

describe('computeReelSetStats', () => {
  it('updates counts and duplicate summary', () => {
    const document = parseCanonicalJson(canonicalJson, 'runtime-core@1.8.0')
    const reelSet = document.reelSets.base_game!
    const stats = computeReelSetStats(reelSet)
    expect(stats.reels).toHaveLength(5)
    expect(stats.reels[0]?.length).toBe(5)
    expect(stats.totals.totalSymbols).toBe(25)
    expect(stats.totals.symbolCounts.find((item) => item.symbolId === 'L1')?.count).toBeGreaterThan(
      0,
    )
    expect(stats.reels[0]?.duplicateSymbolIds.length).toBeGreaterThan(0)
  })

  it('reflects edits in statistics', () => {
    const document = parseCanonicalJson(canonicalJson, 'runtime-core@1.8.0')
    const updated = removeSymbolFromReel(document, 0, 0)
    const reelSet = updated.reelSets.base_game!
    const stats = computeReelSetStats(reelSet)
    expect(stats.reels[0]?.length).toBe(4)
  })

  it('handles empty reels', () => {
    const stats = computeReelSetStats({
      id: 'empty',
      reels: [{ reelIndex: 0, symbols: [] }],
    })
    expect(stats.reels[0]?.length).toBe(0)
    expect(stats.totals.totalSymbols).toBe(0)
  })
})

describe('drag event helpers', () => {
  const document = parseCanonicalJson(canonicalJson, 'runtime-core@1.8.0')

  it('resolves drag overlay labels', () => {
    const label = resolveDragOverlayLabel(
      {
        active: { data: { current: { symbolId: 'H1' } } },
      } as never,
      document.symbols,
    )
    expect(label).toBe('High 1')
  })

  it('returns null for unknown drag payloads', () => {
    const label = resolveDragOverlayLabel(
      { active: { data: { current: {} } } } as never,
      document.symbols,
    )
    expect(label).toBeNull()
  })

  it('resolves drag end ids', () => {
    expect(
      resolveDragEndIds({
        active: { id: 'slot-0-1' },
        over: { id: 'slot-1-0' },
      } as never),
    ).toEqual({ activeId: 'slot-0-1', overId: 'slot-1-0' })
    expect(
      resolveDragEndIds({
        active: { id: 'slot-0-1' },
        over: null,
      } as never),
    ).toEqual({ activeId: 'slot-0-1', overId: null })
  })
})

describe('mutation edge cases', () => {
  it('handles invalid duplicate and parse failures', () => {
    const document = parseCanonicalJson(canonicalJson, 'runtime-core@1.8.0')
    const dup = duplicateSymbolOnReel(document, 0, 99)
    expect(dup.reelSets.base_game?.reels[0]?.symbols).toEqual(
      document.reelSets.base_game?.reels[0]?.symbols,
    )
    expect(parseSlotId('bad-id')).toBeNull()
    expect(parsePaletteId('not-palette')).toBeNull()
  })

  it('serializes weights when present', () => {
    const document = parseCanonicalJson(
      {
        reelSets: {
          base_game: {
            id: 'base_game',
            reels: [{ reelIndex: 0, symbols: ['A'], weights: [5] }],
          },
        },
      },
      'runtime-core@1.8.0',
    )
    const merged = mergeReelSetsIntoCanonical(
      { schemaVersion: '1.0.0', reelSets: {} },
      document.reelSets,
    )
    const reelSets = merged.reelSets as Record<
      string,
      { reels: Array<{ weights?: number[] }> }
    >
    expect(reelSets.base_game.reels[0]?.weights).toEqual([5])
  })
})

describe('symbol colors', () => {
  it('normalizes symbol types and returns badge classes', () => {
    expect(normalizeSymbolType('wild')).toBe('wild')
    expect(normalizeSymbolType('unknown')).toBe('regular')
    expect(symbolTypeBadgeClass('scatter')).toContain('primary')
  })
})
