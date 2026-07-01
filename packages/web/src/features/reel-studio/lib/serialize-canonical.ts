import type { StudioReelSet } from '@/features/reel-studio/types'

function serializeReelSet(reelSet: StudioReelSet): Record<string, unknown> {
  return {
    id: reelSet.id,
    reels: reelSet.reels.map((reel) => {
      const payload: Record<string, unknown> = {
        reelIndex: reel.reelIndex,
        symbols: [...reel.symbols],
      }
      if (reel.weights && reel.weights.length > 0) {
        payload.weights = [...reel.weights]
      }
      return payload
    }),
  }
}

export function serializeReelSets(
  reelSets: Record<string, StudioReelSet>,
): Record<string, unknown> {
  const serialized: Record<string, unknown> = {}
  for (const [key, reelSet] of Object.entries(reelSets)) {
    serialized[key] = serializeReelSet(reelSet)
  }
  return serialized
}

/** Merge edited reel sets into the source canonical JSON; all other keys are preserved in order. */
export function mergeReelSetsIntoCanonical(
  originalCanonicalJson: Record<string, unknown>,
  reelSets: Record<string, StudioReelSet>,
): Record<string, unknown> {
  const serialized = serializeReelSets(reelSets)
  const merged: Record<string, unknown> = {}
  let wroteReelSets = false
  for (const [key, value] of Object.entries(originalCanonicalJson)) {
    if (key === 'reelSets') {
      merged[key] = serialized
      wroteReelSets = true
    } else {
      merged[key] = value
    }
  }
  if (!wroteReelSets) {
    merged.reelSets = serialized
  }
  return merged
}
