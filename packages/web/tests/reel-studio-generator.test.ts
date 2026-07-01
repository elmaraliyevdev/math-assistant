import { describe, expect, it } from 'vitest'

import { buildDiffSet, diffReels, rankCandidates, summarizeCandidate } from '@/features/reel-studio/generator/candidate'
import {
  buildPerReelDistribution,
  buildSymbolPool,
  computeDistribution,
  distributeCountsAcrossReels,
} from '@/features/reel-studio/generator/distribution'
import { buildGeneratorInput, generateCandidates } from '@/features/reel-studio/generator/generator'
import { buildHeatmaps, mergeHeatmapLayers } from '@/features/reel-studio/generator/heatmap'
import { buildSmartSuggestions, computeDesignHealth } from '@/features/reel-studio/generator/health'
import { placePoolOnReels, moveSymbol, reelsToStrips, rotateReel, stripsToReels, swapSymbols } from '@/features/reel-studio/generator/placement'
import { repairReels } from '@/features/reel-studio/generator/repair'
import { createSeededRng, seededInt, shuffleWithSeed } from '@/features/reel-studio/generator/seed'
import { computeCandidateStatistics, scoreCandidate } from '@/features/reel-studio/generator/scoring'
import type { GeneratedCandidate } from '@/features/reel-studio/generator/types'
import { DEFAULT_DESIGN_GOALS } from '@/features/reel-studio/generator/types'
import { createDefaultConstraintDocument } from '@/features/reel-studio/constraints/engine/utils'
import { runConstraintEngine } from '@/features/reel-studio/constraints/engine'
import type { StudioReelSet } from '@/features/reel-studio/types'

const symbols = {
  A: { id: 'A', type: 'regular' as const },
  B: { id: 'B', type: 'regular' as const },
  W: { id: 'W', type: 'wild' as const },
  S: { id: 'S', type: 'scatter' as const },
}

const reelSet: StudioReelSet = {
  id: 'base',
  reels: [
    { reelIndex: 0, symbols: ['A', 'B', 'W', 'A', 'S'] },
    { reelIndex: 1, symbols: ['B', 'A', 'S', 'A', 'B'] },
    { reelIndex: 2, symbols: ['A', 'W', 'B', 'S', 'A'] },
  ],
}

describe('seed', () => {
  it('produces deterministic shuffle', () => {
    const input = ['A', 'B', 'C', 'D', 'E']
    expect(shuffleWithSeed(input, 99)).toEqual(shuffleWithSeed(input, 99))
    expect(shuffleWithSeed(input, 99)).not.toEqual(shuffleWithSeed(input, 100))
  })

  it('creates bounded integers', () => {
    const rng = createSeededRng(7)
    for (let index = 0; index < 20; index += 1) {
      const value = rng()
      expect(value).toBeGreaterThanOrEqual(0)
      expect(value).toBeLessThan(1)
    }
    expect(seededInt(3, 1, 3)).toBeGreaterThanOrEqual(1)
    expect(seededInt(3, 1, 3)).toBeLessThanOrEqual(3)
  })
})

describe('distribution', () => {
  it('builds pools and distributes across reels', () => {
    const document = createDefaultConstraintDocument(['A', 'B', 'W', 'S'], 3)
    document.inventory.W = { symbolId: 'W', reelCounts: {}, totalTarget: 6 }
    document.inventory.S = { symbolId: 'S', reelCounts: {}, totalTarget: 6 }
    const pool = buildSymbolPool(symbols, document, DEFAULT_DESIGN_GOALS, 15)
    expect(pool.length).toBe(15)
    const reels = placePoolOnReels(pool, [5, 5, 5])
    expect(reels.flat().length).toBe(15)
    const distribution = computeDistribution(reels)
    expect(Object.keys(distribution).length).toBeGreaterThan(0)
  })

  it('fills and trims pools from design goals when inventory is empty', () => {
    const document = createDefaultConstraintDocument(['A', 'B', 'W', 'S'], 3)
    const smallPool = buildSymbolPool(symbols, document, DEFAULT_DESIGN_GOALS, 40)
    expect(smallPool.length).toBe(40)
    const largeTargets = createDefaultConstraintDocument(['A', 'B'], 2)
    largeTargets.inventory.A = { symbolId: 'A', reelCounts: {}, totalTarget: 50 }
    largeTargets.inventory.B = { symbolId: 'B', reelCounts: {}, totalTarget: 50 }
    const trimmed = buildSymbolPool(symbols, largeTargets, DEFAULT_DESIGN_GOALS, 20)
    expect(trimmed.length).toBe(20)
  })

  it('distributes counts and per-reel layouts', () => {
    expect(distributeCountsAcrossReels(11, 3)).toEqual([4, 4, 3])
    const perReel = buildPerReelDistribution(['A', 'B', 'C', 'D', 'E', 'F'], 2, [3, 3])
    expect(perReel[0]).toEqual(['A', 'B', 'C'])
    expect(perReel[1]).toEqual(['D', 'E', 'F'])
  })
})

describe('placement and repair', () => {
  it('swaps and rotates reels', () => {
    const reels = [
      ['A', 'B', 'C'],
      ['D', 'E', 'F'],
    ]
    const swapped = swapSymbols(reels, 0, 0, 1, 2)
    expect(swapped[0]![0]).toBe('F')
    expect(swapped[1]![2]).toBe('A')
    const rotated = rotateReel(reels, 0, 1)
    expect(rotated[0]).toEqual(['B', 'C', 'A'])
  })

  it('moves symbols and converts strip formats', () => {
    const reels = [
      ['A', 'B', 'C'],
      ['D', 'E', 'F'],
    ]
    const moved = moveSymbol(reels, 0, 0, 1, 1)
    expect(moved[0]).toEqual(['B', 'C'])
    expect(moved[1]).toEqual(['D', 'A', 'E', 'F'])
    const strips = reelsToStrips(reels)
    expect(stripsToReels(strips)).toEqual(reels)
    expect(swapSymbols(reels, 9, 0, 0, 0)).toEqual(reels)
  })

  it('repairs without increasing violations indefinitely', () => {
    const document = createDefaultConstraintDocument(['A', 'B', 'W', 'S'], 3)
    document.constraints.push({
      id: 'max-w',
      type: 'max_consecutive',
      enabled: true,
      description: 'Wild streak',
      targetType: 'symbol',
      targetId: 'W',
      value: 1,
      scope: 'global',
      severity: 'error',
    })
    const reels = [
      ['W', 'W', 'A', 'B', 'S'],
      ['A', 'B', 'S', 'A', 'B'],
      ['A', 'W', 'B', 'S', 'A'],
    ]
    const repaired = repairReels(reels, symbols, document, 42, 80)
    expect(repaired.repairCount).toBeGreaterThanOrEqual(0)
    expect(repaired.reels.flat().length).toBe(15)
  })
})

describe('scoring and health', () => {
  it('scores candidates and computes design health', () => {
    const document = createDefaultConstraintDocument(['A', 'B', 'W', 'S'], 3)
    const reels = reelSet.reels.map((reel) => reel.symbols)
    const score = scoreCandidate(reels, symbols, document, 2)
    expect(score.total).toBeGreaterThan(0)
    expect(score.total).toBeLessThanOrEqual(100)
    const stats = computeCandidateStatistics(
      reels,
      symbols,
      document.groups,
      document.edgeWrapping,
    )
    expect(stats.symbolCounts.A).toBeGreaterThan(0)
    const health = computeDesignHealth(reelSet, symbols, document)
    expect(health.overallScore).toBeGreaterThan(0)
    expect(health.metrics.length).toBeGreaterThan(0)
  })

  it('builds smart suggestions from violations', () => {
    const document = createDefaultConstraintDocument(['A', 'B', 'W', 'S'], 3)
    document.constraints.push({
      id: 'max-w',
      type: 'max_consecutive',
      enabled: true,
      description: 'Wild streak',
      targetType: 'symbol',
      targetId: 'W',
      value: 1,
      scope: 'global',
      severity: 'error',
    })
    const badSet: StudioReelSet = {
      id: 'bad',
      reels: [{ reelIndex: 0, symbols: ['W', 'W', 'A'] }],
    }
    const suggestions = buildSmartSuggestions(badSet, symbols, document)
    expect(suggestions.length).toBeGreaterThan(0)
  })

  it('recommends inventory and balance fixes', () => {
    const document = createDefaultConstraintDocument(['A', 'B', 'W', 'S'], 3)
    document.inventory.S = { symbolId: 'S', reelCounts: {}, totalTarget: 10 }
    document.constraints.push({
      id: 'dist-s',
      type: 'min_distance',
      enabled: true,
      description: 'Scatter spacing',
      targetType: 'symbol',
      targetId: 'S',
      value: 3,
      scope: 'global',
      severity: 'warning',
    })
    const clustered: StudioReelSet = {
      id: 'clustered',
      reels: [
        { reelIndex: 0, symbols: ['S', 'S', 'A', 'B', 'A'] },
        { reelIndex: 1, symbols: ['A', 'B', 'A', 'B', 'A'] },
        { reelIndex: 2, symbols: ['B', 'A', 'B', 'A', 'B'] },
      ],
    }
    const health = computeDesignHealth(clustered, symbols, document)
    expect(health.recommendations.length).toBeGreaterThan(0)
  })
})

describe('heatmaps and candidate diff', () => {
  it('builds heatmaps and diffs reels', () => {
    const document = createDefaultConstraintDocument(['A', 'B', 'W', 'S'], 3)
    const reels = reelSet.reels.map((reel) => reel.symbols)
    const validation = runConstraintEngine({ reelSet, symbols, constraintDocument: document })
    const heatmaps = buildHeatmaps(reels, symbols, validation, true)
    const merged = mergeHeatmapLayers(heatmaps)
    expect(Object.keys(merged).length).toBeGreaterThanOrEqual(0)

    const wildHeavy = [
      ['W', 'W', 'A', 'S', 'A'],
      ['S', 'A', 'B', 'S', 'A'],
      ['A', 'W', 'B', 'S', 'A'],
    ]
    const wildHeatmaps = buildHeatmaps(wildHeavy, symbols, validation, false)
    expect(Object.keys(wildHeatmaps.wildClustering).length).toBeGreaterThan(0)

    const changes = diffReels(reelSet.reels, [
      { reelIndex: 0, symbols: ['B', 'B', 'W', 'A', 'S'] },
      ...reelSet.reels.slice(1),
    ])
    expect(changes.length).toBeGreaterThan(0)
    expect(buildDiffSet(changes).size).toBe(changes.length)
  })

  it('summarizes and ranks candidates', () => {
    const base: GeneratedCandidate = {
      id: 'a',
      reels: reelSet.reels,
      qualityScore: 98,
      violations: 0,
      warnings: 0,
      statistics: {
        entropy: 2,
        duplicatePercent: 0,
        symbolCounts: {},
        reelLengths: [5, 5, 5],
      },
      heatmaps: { wildClustering: {}, scatterSpacing: {}, violationIntensity: {} },
      distribution: {},
      generationTimeMs: 1,
      seed: 1,
      repairCount: 0,
      summary: '',
    }
    expect(summarizeCandidate(base)).toContain('Perfect')
    expect(
      summarizeCandidate({ ...base, qualityScore: 92, repairCount: 12 }).length,
    ).toBeGreaterThan(0)
    expect(rankCandidates([{ ...base, qualityScore: 80, id: 'b' }, base])[0]!.id).toBe('a')
  })
})

describe('generator', () => {
  it('generates deterministic ranked candidates', () => {
    const document = createDefaultConstraintDocument(['A', 'B', 'W', 'S'], 3)
    const input = buildGeneratorInput({
      reelCount: 3,
      reelLengths: [5, 5, 5],
      symbols,
      constraintDocument: document,
      designGoals: DEFAULT_DESIGN_GOALS,
      seed: 1234,
      candidateCount: 3,
    })
    const first = generateCandidates(input)
    const second = generateCandidates(input)
    expect(first.ranking).toEqual(second.ranking)
    expect(first.candidates[0]?.reels.flatMap((reel) => reel.symbols).length).toBe(15)
    const ranked = rankCandidates(first.candidates)
    expect(ranked[0]!.qualityScore).toBeGreaterThanOrEqual(ranked[ranked.length - 1]!.qualityScore)
  })

  it('produces candidates with statistics and scores', () => {
    const document = createDefaultConstraintDocument(['A', 'B', 'W', 'S'], 5)
    const input = buildGeneratorInput({
      reelCount: 5,
      reelLengths: [8, 8, 8, 8, 8],
      symbols,
      constraintDocument: document,
      designGoals: { ...DEFAULT_DESIGN_GOALS, reelCount: 5, reelLength: 8 },
      seed: 77,
      candidateCount: 2,
    })
    const report = generateCandidates(input)
    expect(report.candidates).toHaveLength(2)
    for (const candidate of report.candidates) {
      expect(candidate.qualityScore).toBeGreaterThan(0)
      expect(candidate.statistics.reelLengths).toEqual([8, 8, 8, 8, 8])
      expect(candidate.summary.length).toBeGreaterThan(0)
    }
  })
})
