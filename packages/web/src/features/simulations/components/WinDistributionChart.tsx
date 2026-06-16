import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { SimulationResults } from '@/types/api'
import { chartMargin, chartTheme } from '@/features/simulations/utils/chart-theme'
import { formatPercent } from '@/lib/utils'

interface WinDistributionChartProps {
  distribution: SimulationResults['winDistribution']
}

export function WinDistributionChart({ distribution }: WinDistributionChartProps) {
  const data = distribution.buckets.map((bucket) => ({
    name: bucket.label,
    count: bucket.count,
    percentage: bucket.percentage,
  }))

  if (data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Win distribution</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Win distribution is unavailable for this simulation run.
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Win distribution</CardTitle>
      </CardHeader>
      <CardContent className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={chartMargin}>
            <CartesianGrid stroke={chartTheme.border} strokeDasharray="3 3" />
            <XAxis
              dataKey="name"
              tick={{ fill: chartTheme.muted, fontSize: 12 }}
              axisLine={{ stroke: chartTheme.border }}
              tickLine={{ stroke: chartTheme.border }}
            />
            <YAxis
              tick={{ fill: chartTheme.muted, fontSize: 12 }}
              axisLine={{ stroke: chartTheme.border }}
              tickLine={{ stroke: chartTheme.border }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: chartTheme.card,
                borderColor: chartTheme.border,
                color: chartTheme.foreground,
              }}
              formatter={(value: number, _name, item) => [
                `${value} spins (${formatPercent(item.payload.percentage)})`,
                'Count',
              ]}
            />
            <Bar dataKey="count" fill={chartTheme.primary} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
