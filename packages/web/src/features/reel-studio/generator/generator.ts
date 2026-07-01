import { runConstraintEngine } from '@/features/reel-studio/constraints/engine'
import { buildSymbolPool, computeDistribution } from '@/features/reel-studio/generator/distribution'
import { buildHeatmaps } from '@/features/reel-studio/generator/heatmap'
import { placePoolOnReels, reelsToStrips } from '@/features/reel-studio/generator/placement'
import { repairReels } from '@/features/reel-studio/generator/repair'
import { rankCandidates, summarizeCandidate } from '@/features/reel-studio/generator/candidate'
import { shuffleWithSeed } from '@/features/reel-studio/generator/seed'
import { computeCandidateStatistics, scoreCandidate } from '@/features/reel-studio/generator/scoring'
import type {
  GeneratedCandidate,
  GenerationReport,
  GeneratorInput,
  GeneratorStrategy,
} from '@/features/reel-studio/generator/types'

function generateSingleCandidate(
  input: GeneratorInput,
  candidateSeed: number,
  candidateIndex: number,
): GeneratedCandidate {
  const started = performance.now()
  const totalLength = input.reelLengths.reduce((sum, length) => sum + length, 0)
  const pool = buildSymbolPool(
    input.symbols,
    input.constraintDocument,
    input.designGoals,
    totalLength,
  )
  const shuffled = shuffleWithSeed(pool, candidateSeed)
  let reels = placePoolOnReels(shuffled, input.reelLengths)
  const repaired = repairReels(
    reels,
    input.symbols,
    input.constraintDocument,
    candidateSeed + 17,
    input.maxRepairIterations,
  )
  reels = repaired.reels

  const strips = reelsToStrips(reels)
  const reelSet = { id: `candidate-${candidateIndex}`, reels: strips }
  const validation = runConstraintEngine({
    reelSet,
    symbols: input.symbols,
    constraintDocument: input.constraintDocument,
  })
  const score = scoreCandidate(reels, input.symbols, input.constraintDocument, repaired.repairCount)
  const statistics = computeCandidateStatistics(
    reels,
    input.symbols,
    input.constraintDocument.groups,
    input.constraintDocument.edgeWrapping,
  )
  const heatmaps = buildHeatmaps(
    reels,
    input.symbols,
    validation,
    input.constraintDocument.edgeWrapping,
  )
  const distribution = computeDistribution(reels)
  const generationTimeMs = performance.now() - started

  const candidate: GeneratedCandidate = {
    id: `candidate-${candidateIndex}-${candidateSeed}`,
    reels: strips,
    qualityScore: Math.round(score.total),
    violations: validation.summary.error,
    warnings: validation.summary.warning,
    statistics,
    heatmaps,
    distribution,
    generationTimeMs,
    seed: candidateSeed,
    repairCount: repaired.repairCount,
    summary: '',
  }
  candidate.summary = summarizeCandidate(candidate)
  return candidate
}

export class DeterministicGeneratorStrategy implements GeneratorStrategy {
  generate(input: GeneratorInput): GenerationReport {
    const started = performance.now()
    const count = Math.max(1, input.candidateCount)
    const candidates: GeneratedCandidate[] = []
    for (let index = 0; index < count; index += 1) {
      const candidateSeed = input.seed + index * 9973
      candidates.push(generateSingleCandidate(input, candidateSeed, index))
    }
    const ranked = rankCandidates(candidates)
    return {
      candidates: ranked,
      generationTimeMs: performance.now() - started,
      seed: input.seed,
      ranking: ranked.map((candidate) => candidate.id),
    }
  }
}

export function generateCandidates(input: GeneratorInput): GenerationReport {
  return new DeterministicGeneratorStrategy().generate(input)
}

export function buildGeneratorInput(
  partial: Omit<GeneratorInput, 'maxRepairIterations' | 'candidateCount'> & {
    maxRepairIterations?: number
    candidateCount?: number
  },
): GeneratorInput {
  return {
    ...partial,
    candidateCount: partial.candidateCount ?? 3,
    maxRepairIterations: partial.maxRepairIterations ?? 120,
  }
}
