import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { buildComparisonDeltas } from '@/features/workbench/comparison-deltas'
import type { SimulationCompareResponse } from '@/types/api'
import { formatPercent } from '@/lib/utils'

interface ComparisonDeltaSummaryProps {
  data: SimulationCompareResponse
}

export function ComparisonDeltaSummary({ data }: ComparisonDeltaSummaryProps) {
  const rows = buildComparisonDeltas(data)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Delta metrics</CardTitle>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-muted-foreground">
              <th className="pb-2 pr-4 font-medium">Run</th>
              <th className="pb-2 pr-4 font-medium">RTP Δ</th>
              <th className="pb-2 pr-4 font-medium">Volatility Δ</th>
              <th className="pb-2 pr-4 font-medium">Hit frequency Δ</th>
              <th className="pb-2 font-medium">Feature freq. Δ</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.simulationId} className="border-b last:border-0">
                <td className="py-3 pr-4 font-medium">{row.label}</td>
                <td className="py-3 pr-4">{formatDelta(row.rtpDelta, true)}</td>
                <td className="py-3 pr-4">{formatDelta(row.volatilityDelta)}</td>
                <td className="py-3 pr-4">{formatDelta(row.hitFrequencyDelta, true)}</td>
                <td className="py-3">{formatDelta(row.featureFrequencyDelta, true)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  )
}

function formatDelta(value: number | null, asPercent = false): string {
  if (value == null) {
    return 'baseline'
  }
  const formatted = asPercent ? formatPercent(value) : value.toFixed(3)
  return value > 0 ? `+${formatted}` : formatted
}
