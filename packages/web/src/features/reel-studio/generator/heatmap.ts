import { positionKey } from '@/features/reel-studio/constraints/types'
import type { ConstraintValidationReport } from '@/features/reel-studio/constraints/types'
import type { CandidateHeatmaps } from '@/features/reel-studio/generator/types'
import type { StudioSymbol } from '@/features/reel-studio/types'

function clusterIntensity(reel: string[], symbolId: string): Record<string, number> {
  const intensities: Record<string, number> = {}
  let streak = 0
  for (let index = 0; index < reel.length; index += 1) {
    if (reel[index] === symbolId) {
      streak += 1
      if (streak > 1) {
        intensities[positionKey(0, index)] = Math.min(1, streak / 4)
      }
    } else {
      streak = 0
    }
  }
  return intensities
}

function spacingIntensity(reel: string[], symbolId: string, wrap: boolean): Record<string, number> {
  const intensities: Record<string, number> = {}
  const indices = reel
    .map((id, index) => (id === symbolId ? index : -1))
    .filter((index) => index >= 0)
  for (let index = 0; index < indices.length; index += 1) {
    const current = indices[index]!
    const next = indices[index + 1]
    if (next === undefined) {
      continue
    }
    const linear = next - current - 1
    const forward = wrap ? (next - current + reel.length) % reel.length - 1 : linear
    const distance = Math.max(0, Math.min(linear, forward))
    if (distance < 3) {
      intensities[positionKey(0, current)] = 1 - distance / 3
      intensities[positionKey(0, next)] = 1 - distance / 3
    }
  }
  return intensities
}

export function buildHeatmaps(
  reels: string[][],
  symbols: Record<string, StudioSymbol>,
  validation: ConstraintValidationReport,
  edgeWrapping: boolean,
): CandidateHeatmaps {
  const wildClustering: Record<string, number> = {}
  const scatterSpacing: Record<string, number> = {}
  const violationIntensity: Record<string, number> = {}

  const wildIds = Object.entries(symbols)
    .filter(([, symbol]) => symbol.type === 'wild')
    .map(([id]) => id)
  const scatterIds = Object.entries(symbols)
    .filter(([, symbol]) => symbol.type === 'scatter')
    .map(([id]) => id)

  reels.forEach((reel, reelIndex) => {
    for (const wildId of wildIds) {
      const local = clusterIntensity(reel, wildId)
      for (const [key, value] of Object.entries(local)) {
        const [, pos] = key.split(':')
        wildClustering[positionKey(reelIndex, Number(pos))] = value
      }
    }
    for (const scatterId of scatterIds) {
      const local = spacingIntensity(reel, scatterId, edgeWrapping)
      for (const [key, value] of Object.entries(local)) {
        const [, pos] = key.split(':')
        scatterSpacing[positionKey(reelIndex, Number(pos))] = value
      }
    }
  })

  for (const [key, items] of Object.entries(validation.violationsByPosition)) {
    violationIntensity[key] = Math.min(1, items.length / 3)
  }

  return { wildClustering, scatterSpacing, violationIntensity }
}

export function mergeHeatmapLayers(
  heatmaps: CandidateHeatmaps,
): Record<string, { wild: number; scatter: number; violation: number }> {
  const keys = new Set([
    ...Object.keys(heatmaps.wildClustering),
    ...Object.keys(heatmaps.scatterSpacing),
    ...Object.keys(heatmaps.violationIntensity),
  ])
  const merged: Record<string, { wild: number; scatter: number; violation: number }> = {}
  for (const key of keys) {
    merged[key] = {
      wild: heatmaps.wildClustering[key] ?? 0,
      scatter: heatmaps.scatterSpacing[key] ?? 0,
      violation: heatmaps.violationIntensity[key] ?? 0,
    }
  }
  return merged
}
