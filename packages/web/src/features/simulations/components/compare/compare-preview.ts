import { formatPercent } from '@/lib/utils'
import { buildComparisonDeltas } from '@/features/workbench/comparison-deltas'
import type { SimulationCompareResponse } from '@/types/api'

type PreviewMetric = {
  label: string
  values: Array<{ id: string; label: string; value: string }>
  deltas?: Array<{ id: string; delta: string }>
}

export function buildComparePreviewMetrics(
  data: SimulationCompareResponse,
): PreviewMetric[] {
  const rows = buildComparisonDeltas(data)

  return [
    {
      label: 'RTP',
      values: rows.map((row) => ({
        id: row.simulationId,
        label: row.label,
        value: formatPercent(row.rtp),
      })),
      deltas: rows
        .filter((row) => row.rtpDelta != null)
        .map((row) => ({
          id: row.simulationId,
          delta:
            row.rtpDelta! > 0
              ? `+${formatPercent(row.rtpDelta!)}`
              : formatPercent(row.rtpDelta!),
        })),
    },
    {
      label: 'Volatility',
      values: rows.map((row) => ({
        id: row.simulationId,
        label: row.label,
        value: row.volatility.toFixed(3),
      })),
      deltas: rows
        .filter((row) => row.volatilityDelta != null)
        .map((row) => ({
          id: row.simulationId,
          delta:
            row.volatilityDelta! > 0
              ? `+${row.volatilityDelta!.toFixed(3)}`
              : row.volatilityDelta!.toFixed(3),
        })),
    },
    {
      label: 'Hit rate',
      values: rows.map((row) => ({
        id: row.simulationId,
        label: row.label,
        value: formatPercent(row.hitFrequency),
      })),
      deltas: rows
        .filter((row) => row.hitFrequencyDelta != null)
        .map((row) => ({
          id: row.simulationId,
          delta:
            row.hitFrequencyDelta! > 0
              ? `+${formatPercent(row.hitFrequencyDelta!)}`
              : formatPercent(row.hitFrequencyDelta!),
        })),
    },
    {
      label: 'Feature frequency',
      values: rows.map((row) => {
        const entry = data.simulations.find((item) => item.simulationId === row.simulationId)
        const avg =
          entry && entry.results.featureFrequencies.length > 0
            ? entry.results.featureFrequencies.reduce((sum, item) => sum + item.frequency, 0) /
              entry.results.featureFrequencies.length
            : null
        return {
          id: row.simulationId,
          label: row.label,
          value: avg != null ? formatPercent(avg) : '—',
        }
      }),
      deltas: rows
        .filter((row) => row.featureFrequencyDelta != null)
        .map((row) => ({
          id: row.simulationId,
          delta:
            row.featureFrequencyDelta! > 0
              ? `+${formatPercent(row.featureFrequencyDelta!)}`
              : formatPercent(row.featureFrequencyDelta!),
        })),
    },
  ]
}
