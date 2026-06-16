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
import { chartMargin, chartTheme } from '@/features/simulations/utils/chart-theme'
import type { SimulationResults } from '@/types/api'
import { formatPercent } from '@/lib/utils'

interface JackpotFrequencyChartProps {
  jackpots: SimulationResults['jackpotFrequencies']
}

export function JackpotFrequencyChart({
  jackpots,
}: JackpotFrequencyChartProps) {
  const data = jackpots.map((jackpot) => ({
    name: jackpot.jackpotTier,
    frequency: jackpot.frequency,
    oneInX: jackpot.oneInX,
    triggerCount: jackpot.triggerCount,
  }))

  if (data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Jackpot frequency</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            No jackpot hits recorded for this simulation.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Jackpot frequency</CardTitle>
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
              tickFormatter={(value) => formatPercent(value, 1)}
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
              formatter={(value: number, _name, item) => {
                const oneInX = item.payload.oneInX
                const suffix =
                  oneInX != null ? ` · 1 in ${oneInX.toFixed(1)}` : ''
                return [`${formatPercent(value)}${suffix}`, 'Frequency']
              }}
            />
            <Bar
              dataKey="frequency"
              fill={chartTheme.primary}
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
