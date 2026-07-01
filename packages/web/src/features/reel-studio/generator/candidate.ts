import type { StudioReelStrip } from '@/features/reel-studio/types'
import type { CandidateDiffPosition, GeneratedCandidate } from '@/features/reel-studio/generator/types'

export function diffReels(
  before: StudioReelStrip[],
  after: StudioReelStrip[],
): CandidateDiffPosition[] {
  const changes: CandidateDiffPosition[] = []
  const maxReels = Math.max(before.length, after.length)
  for (let reelIndex = 0; reelIndex < maxReels; reelIndex += 1) {
    const left = before[reelIndex]?.symbols ?? []
    const right = after[reelIndex]?.symbols ?? []
    const maxLen = Math.max(left.length, right.length)
    for (let symbolIndex = 0; symbolIndex < maxLen; symbolIndex += 1) {
      const prev = left[symbolIndex] ?? null
      const next = right[symbolIndex] ?? null
      if (prev !== next) {
        changes.push({ reelIndex, symbolIndex, before: prev, after: next })
      }
    }
  }
  return changes
}

export function rankCandidates(candidates: GeneratedCandidate[]): GeneratedCandidate[] {
  return [...candidates].sort((a, b) => {
    if (b.qualityScore !== a.qualityScore) {
      return b.qualityScore - a.qualityScore
    }
    if (a.violations !== b.violations) {
      return a.violations - b.violations
    }
    return a.repairCount - b.repairCount
  })
}

export function summarizeCandidate(candidate: GeneratedCandidate): string {
  if (candidate.violations === 0 && candidate.qualityScore >= 95) {
    return 'Perfect balance'
  }
  if (candidate.qualityScore >= 90) {
    return 'Strong spacing and balance'
  }
  if (candidate.repairCount > 10) {
    return 'Higher feature density'
  }
  return 'Lower clustering profile'
}

export function buildDiffSet(changes: CandidateDiffPosition[]): Set<string> {
  return new Set(changes.map((change) => `${change.reelIndex}:${change.symbolIndex}`))
}
