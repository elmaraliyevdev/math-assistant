import type { SimulationCompareResponse } from '@/types/api'

export interface ComparisonDeltaRow {
  simulationId: string
  label: string
  rtp: number
  rtpDelta: number | null
  volatility: number
  volatilityDelta: number | null
  hitFrequency: number
  hitFrequencyDelta: number | null
  featureFrequencyDelta: number | null
}

export function buildComparisonDeltas(
  data: SimulationCompareResponse,
): ComparisonDeltaRow[] {
  if (data.simulations.length === 0) {
    return []
  }

  const baseline = data.simulations[0]
  const baselineRtp = baseline.results.summary.rtp
  const baselineVolatility = baseline.results.summary.volatility
  const baselineHit = baseline.results.summary.hitFrequency
  const baselineFeature = averageFeatureFrequency(baseline.results.featureFrequencies)

  return data.simulations.map((entry, index) => {
    const label =
      entry.gameName && entry.gameVersionLabel
        ? `${entry.gameName} ${entry.gameVersionLabel}`
        : entry.gameName ?? `Run ${index + 1}`
    const featureFrequency = averageFeatureFrequency(entry.results.featureFrequencies)

    return {
      simulationId: entry.simulationId,
      label,
      rtp: entry.results.summary.rtp,
      rtpDelta: index === 0 ? null : entry.results.summary.rtp - baselineRtp,
      volatility: entry.results.summary.volatility,
      volatilityDelta:
        index === 0 ? null : entry.results.summary.volatility - baselineVolatility,
      hitFrequency: entry.results.summary.hitFrequency,
      hitFrequencyDelta:
        index === 0 ? null : entry.results.summary.hitFrequency - baselineHit,
      featureFrequencyDelta:
        index === 0 || baselineFeature === null || featureFrequency === null
          ? null
          : featureFrequency - baselineFeature,
    }
  })
}

function averageFeatureFrequency(
  frequencies: Array<{ frequency: number }>,
): number | null {
  if (frequencies.length === 0) {
    return null
  }
  const total = frequencies.reduce((sum, item) => sum + item.frequency, 0)
  return total / frequencies.length
}
