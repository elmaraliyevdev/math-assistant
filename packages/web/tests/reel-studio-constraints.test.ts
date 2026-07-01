import { describe, expect, it } from 'vitest'

import { runConstraintEngine, validateConstraint } from '@/features/reel-studio/constraints/engine'
import { createDefaultConstraintDocument } from '@/features/reel-studio/constraints/engine/utils'
import {
  circularDistance,
  countSymbolsGlobal,
  findStreakViolations,
  getAdjacentIndices,
  longestStreak,
} from '@/features/reel-studio/constraints/engine/utils'
import { computeAdvancedStatistics } from '@/features/reel-studio/constraints/lib/advanced-statistics'
import { hydratePresetGroups, listPresets } from '@/features/reel-studio/constraints/lib/presets'
import {
  duplicatePreset,
  exportPreset,
  importPreset,
  parseConstraintDocument,
  serializeConstraintDocument,
} from '@/features/reel-studio/constraints/lib/serialize'
import { createUndoStack, pushUndoStack, redoStack, undoStack } from '@/features/reel-studio/constraints/lib/undo-stack'
import type { ConstraintRule } from '@/features/reel-studio/constraints/types'
import type { StudioReelSet } from '@/features/reel-studio/types'

const symbols = {
  A: { id: 'A', type: 'regular' as const },
  B: { id: 'B', type: 'regular' as const },
  W: { id: 'W', type: 'wild' as const },
  S: { id: 'S', type: 'scatter' as const },
}

const reelSet: StudioReelSet = {
  id: 'base_game',
  reels: [
    { reelIndex: 0, symbols: ['S', 'A', 'A', 'B', 'S'] },
    { reelIndex: 1, symbols: ['W', 'W', 'A', 'B', 'A'] },
    { reelIndex: 2, symbols: ['A', 'B', 'S', 'A', 'B'] },
  ],
}

function rule(partial: Partial<ConstraintRule> & Pick<ConstraintRule, 'type' | 'targetId'>): ConstraintRule {
  return {
    id: partial.id ?? `rule-${partial.type}`,
    enabled: true,
    description: partial.description ?? partial.type,
    targetType: partial.targetType ?? 'symbol',
    value: partial.value ?? 1,
    scope: partial.scope ?? 'global',
    severity: partial.severity ?? 'error',
    ...partial,
  }
}

describe('constraint engine utils', () => {
  it('computes counts and streaks', () => {
    expect(countSymbolsGlobal(reelSet.reels, 'symbol', 'S', [], symbols)).toBe(3)
    expect(longestStreak(reelSet.reels[0]!, 'symbol', 'A', [], symbols)).toBe(2)
    expect(circularDistance(5, 0, 4, true)).toBe(1)
  })

  it('creates default documents', () => {
    const doc = createDefaultConstraintDocument(['A', 'B'], 3)
    expect(doc.inventory.A?.reelCounts['0']).toBe(0)
    expect(doc.edgeWrapping).toBe(true)
  })

  it('handles adjacency helpers and streak violations', () => {
    expect(getAdjacentIndices(5, 0, false)).toEqual({ prev: null, next: 1 })
    expect(getAdjacentIndices(1, 0, false)).toEqual({ prev: null, next: null })
    const violation = findStreakViolations(
      reelSet.reels[1]!,
      1,
      'symbol',
      'W',
      [],
      symbols,
      1,
    )
    expect(violation?.length).toBe(2)
  })
})

describe('count constraints', () => {
  const base = createDefaultConstraintDocument(Object.keys(symbols), 3)

  it('validates min, max, and exact count', () => {
    const min = validateConstraint(rule({ type: 'min_count', targetId: 'S', value: 3 }), {
      reelSet,
      symbols,
      constraintDocument: { ...base, constraints: [] },
    })
    expect(min.status).toBe('pass')

    const max = validateConstraint(rule({ type: 'max_count', targetId: 'S', value: 2 }), {
      reelSet,
      symbols,
      constraintDocument: { ...base, constraints: [] },
    })
    expect(max.status).toBe('error')

    const exact = validateConstraint(rule({ type: 'exact_count', targetId: 'S', value: 3 }), {
      reelSet,
      symbols,
      constraintDocument: { ...base, constraints: [] },
    })
    expect(exact.status).toBe('pass')
  })

  it('validates reel-specific count', () => {
    const result = validateConstraint(
      rule({ type: 'reel_specific_count', targetId: 'W', value: 2, reelIndex: 1 }),
      { reelSet, symbols, constraintDocument: { ...base, constraints: [] } },
    )
    expect(result.status).toBe('pass')
  })

  it('validates per-reel scopes and disabled rules', () => {
    const perReel = validateConstraint(
      rule({ type: 'min_count', targetId: 'A', value: 3, scope: 'per_reel' }),
      { reelSet, symbols, constraintDocument: { ...base, constraints: [] } },
    )
    expect(perReel.status).toBe('error')

    const disabled = validateConstraint(
      rule({ type: 'min_count', targetId: 'S', value: 99, enabled: false }),
      { reelSet, symbols, constraintDocument: { ...base, constraints: [] } },
    )
    expect(disabled.message).toContain('disabled')
  })

  it('validates group targets', () => {
    const document = {
      ...base,
      groups: [{ id: 'scatters', name: 'Scatters', symbolIds: ['S'] }],
      constraints: [],
    }
    const result = validateConstraint(
      rule({ type: 'exact_count', targetId: 'scatters', targetType: 'group', value: 3 }),
      { reelSet, symbols, constraintDocument: document },
    )
    expect(result.status).toBe('pass')
  })
})

describe('consecutive constraints', () => {
  const base = createDefaultConstraintDocument(Object.keys(symbols), 3)

  it('validates max consecutive wilds', () => {
    const result = validateConstraint(
      rule({ type: 'max_consecutive', targetId: 'W', value: 1 }),
      { reelSet, symbols, constraintDocument: { ...base, constraints: [] } },
    )
    expect(result.status).toBe('error')
    expect(result.affectedPositions.length).toBeGreaterThan(0)
  })

  it('validates min consecutive', () => {
    const result = validateConstraint(
      rule({ type: 'min_consecutive', targetId: 'A', value: 2 }),
      { reelSet, symbols, constraintDocument: { ...base, constraints: [] } },
    )
    expect(result.status).toBe('pass')
  })
})

describe('distance and adjacency with edge wrapping', () => {
  const base = createDefaultConstraintDocument(Object.keys(symbols), 3)

  it('flags scatter distance violations on circular reel', () => {
    const circular: StudioReelSet = {
      id: 'base_game',
      reels: [{ reelIndex: 0, symbols: ['S', 'A', 'B', 'A', 'S'] }],
    }
    const result = validateConstraint(
      rule({ type: 'min_distance', targetId: 'S', value: 3 }),
      {
        reelSet: circular,
        symbols,
        constraintDocument: { ...base, edgeWrapping: true, constraints: [] },
      },
    )
    expect(result.status).toBe('error')
    expect(result.message).toContain('distance')
  })

  it('flags forbidden adjacency including wrap', () => {
    const circular: StudioReelSet = {
      id: 'base_game',
      reels: [{ reelIndex: 0, symbols: ['S', 'A', 'B', 'A', 'S'] }],
    }
    const result = validateConstraint(
      rule({ type: 'forbidden_adjacency', targetId: 'S' }),
      {
        reelSet: circular,
        symbols,
        constraintDocument: { ...base, edgeWrapping: true, constraints: [] },
      },
    )
    expect(result.status).toBe('error')
  })

  it('validates allowed adjacency whitelist', () => {
    const result = validateConstraint(
      rule({
        type: 'allowed_adjacency',
        targetId: 'W',
        secondaryTargetId: 'A',
        secondaryTargetType: 'symbol',
      }),
      { reelSet, symbols, constraintDocument: { ...base, edgeWrapping: false, constraints: [] } },
    )
    expect(result.status).toBe('error')
  })
})

describe('runConstraintEngine', () => {
  it('aggregates overlapping constraints', () => {
    const document = createDefaultConstraintDocument(Object.keys(symbols), 3)
    document.constraints = [
      rule({ id: '1', type: 'min_count', targetId: 'S', value: 10 }),
      rule({ id: '2', type: 'max_count', targetId: 'S', value: 1 }),
      rule({ id: '3', type: 'min_count', targetId: 'S', value: 1, severity: 'warning' }),
    ]
    const report = runConstraintEngine({ reelSet, symbols, constraintDocument: document })
    expect(report.summary.error).toBeGreaterThanOrEqual(1)
    expect(report.summary.warning).toBeGreaterThanOrEqual(0)
    expect(Object.keys(report.violationsByPosition).length).toBeGreaterThanOrEqual(0)
  })

  it('includes inventory warnings', () => {
    const document = createDefaultConstraintDocument(Object.keys(symbols), 3)
    document.inventory.S = { symbolId: 'S', reelCounts: { '0': 5 }, totalTarget: 5 }
    const report = runConstraintEngine({ reelSet, symbols, constraintDocument: document })
    expect(report.results.some((item) => item.message.includes('Inventory'))).toBe(true)
  })
})

describe('presets and serialization', () => {
  it('hydrates preset groups from symbol types', () => {
    const preset = hydratePresetGroups(
      {
        id: 'generic',
        name: 'Generic',
        description: '',
        builtIn: true,
        document: {
          version: 1,
          edgeWrapping: true,
          groups: [{ id: 'wild', name: 'Wild', symbolIds: [] }],
          inventory: {},
          constraints: [],
        },
      },
      symbols,
    )
    expect(preset.groups[0]?.symbolIds).toContain('W')
  })

  it('lists built-in presets', () => {
    expect(listPresets().length).toBeGreaterThan(5)
  })

  it('round-trips constraint documents', () => {
    const document = createDefaultConstraintDocument(['A'], 1)
    document.constraints = [rule({ type: 'min_count', targetId: 'A', value: 1 })]
    const parsed = parseConstraintDocument(serializeConstraintDocument(document))
    expect(parsed.constraints[0]?.targetId).toBe('A')
  })

  it('imports and duplicates presets', () => {
    const preset = importPreset(
      JSON.stringify({
        id: 'custom',
        name: 'Custom',
        description: 'd',
        builtIn: false,
        document: { version: 1, edgeWrapping: true, groups: [], inventory: {}, constraints: [] },
      }),
    )
    expect(preset.id).toBe('custom')
    const copy = duplicatePreset(preset, 'custom-2', 'Copy')
    expect(copy.name).toBe('Copy')
    expect(exportPreset(copy)).toContain('custom-2')
  })

  it('rejects invalid documents', () => {
    expect(() => parseConstraintDocument('{"version":2}')).toThrow()
    expect(() => importPreset('{}')).toThrow()
  })
})

describe('advanced statistics', () => {
  it('computes entropy and duplicate percent', () => {
    const stats = computeAdvancedStatistics(reelSet, symbols, [], true)
    expect(stats.entropy).toBeGreaterThan(0)
    expect(stats.duplicatePercent).toBeGreaterThan(0)
    expect(stats.longestStreaks.A).toBeGreaterThanOrEqual(2)
  })

  it('handles empty reels', () => {
    const stats = computeAdvancedStatistics(
      { id: 'empty', reels: [{ reelIndex: 0, symbols: [] }] },
      symbols,
      [{ id: 'g', name: 'G', symbolIds: ['A'] }],
      false,
    )
    expect(stats.entropy).toBe(0)
  })
})

describe('undo stack', () => {
  it('supports undo and redo', () => {
    let stack = createUndoStack({ value: 1 })
    stack = pushUndoStack(stack, { value: 2 })
    const undone = undoStack(stack)
    expect(undone?.present.value).toBe(1)
    const redone = redoStack(undone!)
    expect(redone?.present.value).toBe(2)
  })

  it('returns null when stack empty', () => {
    expect(undoStack(createUndoStack(1))).toBeNull()
    const stack = pushUndoStack(createUndoStack(1), 2)
    expect(redoStack(stack)).toBeNull()
  })
})
