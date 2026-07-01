import { runConstraintEngine } from '@/features/reel-studio/constraints/engine'
import type { ConstraintDocument } from '@/features/reel-studio/constraints/types'
import { createSeededRng } from '@/features/reel-studio/generator/seed'
import { moveSymbol, rotateReel, swapSymbols } from '@/features/reel-studio/generator/placement'
import { scoreCandidate } from '@/features/reel-studio/generator/scoring'
import type { StudioSymbol } from '@/features/reel-studio/types'

export interface RepairResult {
  reels: string[][]
  repairCount: number
  score: number
}

function violationCount(
  reels: string[][],
  symbols: Record<string, StudioSymbol>,
  constraintDocument: ConstraintDocument,
): number {
  const report = runConstraintEngine({
    reelSet: {
      id: 'repair',
      reels: reels.map((strip, reelIndex) => ({ reelIndex, symbols: strip })),
    },
    symbols,
    constraintDocument,
  })
  return report.summary.error + report.summary.warning
}

export function repairReels(
  reels: string[][],
  symbols: Record<string, StudioSymbol>,
  constraintDocument: ConstraintDocument,
  seed: number,
  maxIterations: number,
): RepairResult {
  let current = reels.map((reel) => [...reel])
  let repairCount = 0
  const rng = createSeededRng(seed)
  let bestScore = scoreCandidate(current, symbols, constraintDocument, repairCount).total
  let violations = violationCount(current, symbols, constraintDocument)

  for (let iteration = 0; iteration < maxIterations && violations > 0; iteration += 1) {
    const reelCount = current.length
    if (reelCount === 0) {
      break
    }
    const reelA = Math.floor(rng() * reelCount)
    const reelB = Math.floor(rng() * reelCount)
    const lenA = current[reelA]?.length ?? 0
    const lenB = current[reelB]?.length ?? 0
    if (lenA === 0 || lenB === 0) {
      continue
    }
    const posA = Math.floor(rng() * lenA)
    const posB = Math.floor(rng() * lenB)
    const operation = Math.floor(rng() * 3)

    let candidate: string[][]
    if (operation === 0) {
      candidate = swapSymbols(current, reelA, posA, reelB, posB)
    } else if (operation === 1 && reelA !== reelB) {
      candidate = moveSymbol(current, reelA, posA, reelB, posB)
    } else {
      const steps = Math.floor(rng() * (lenA - 1)) + 1
      candidate = rotateReel(current, reelA, steps)
    }

    const nextViolations = violationCount(candidate, symbols, constraintDocument)
    const nextScore = scoreCandidate(candidate, symbols, constraintDocument, repairCount + 1).total
    const improved = nextViolations < violations || (nextViolations === violations && nextScore > bestScore)
    if (improved) {
      current = candidate
      repairCount += 1
      violations = nextViolations
      bestScore = nextScore
    }
  }

  return {
    reels: current,
    repairCount,
    score: bestScore,
  }
}
