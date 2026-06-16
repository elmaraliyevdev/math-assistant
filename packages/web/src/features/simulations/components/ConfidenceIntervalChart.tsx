import {
  CartesianGrid,
  ErrorBar,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { GlossaryTerm } from '@/components/glossary-term'
import type { SimulationResults } from '@/types/api'
import { chartMargin, chartTheme } from '@/features/simulations/utils/chart-theme'
import { formatPercent } from '@/lib/utils'

interface ConfidenceIntervalChartProps {
  interval: SimulationResults['confidenceInterval']
}

export function ConfidenceIntervalChart({ interval }: ConfidenceIntervalChartProps) {
  const margin = interval.upperBound - interval.lowerBound
  const data = [
    {
      name: 'RTP',
      rtp: interval.rtp,
      lower: interval.lowerBound,
      upper: interval.upperBound,
      error: [interval.rtp - interval.lowerBound, interval.upperBound - interval.rtp],
    },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <GlossaryTerm term="confidenceInterval">
            RTP confidence interval ({formatPercent(interval.confidenceLevel, 0)})
          </GlossaryTerm>
        </CardTitle>
      </CardHeader>
      <CardContent className="h-72">
        <div className="mb-4 grid gap-2 text-sm sm:grid-cols-3">
          <p>
            <span className="text-muted-foreground">Lower: </span>
            {formatPercent(interval.lowerBound)}
          </p>
          <p>
            <span className="text-muted-foreground">RTP: </span>
            {formatPercent(interval.rtp)}
          </p>
          <p>
            <span className="text-muted-foreground">Upper: </span>
            {formatPercent(interval.upperBound)}
          </p>
        </div>
        <ResponsiveContainer width="100%" height="calc(100% - 3rem)">
          <LineChart data={data} margin={chartMargin}>
            <CartesianGrid stroke={chartTheme.border} strokeDasharray="3 3" />
            <XAxis
              dataKey="name"
              tick={{ fill: chartTheme.muted, fontSize: 12 }}
              axisLine={{ stroke: chartTheme.border }}
              tickLine={{ stroke: chartTheme.border }}
            />
            <YAxis
              domain={[
                Math.max(0, interval.lowerBound - margin * 0.2),
                interval.upperBound + margin * 0.2,
              ]}
              tickFormatter={(value) => formatPercent(value)}
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
              formatter={(value: number) => [formatPercent(value), 'RTP']}
            />
            <ReferenceLine
              y={interval.rtp}
              stroke={chartTheme.primary}
              strokeDasharray="4 4"
            />
            <Line
              type="monotone"
              dataKey="rtp"
              stroke={chartTheme.primary}
              strokeWidth={2}
              dot={{ fill: chartTheme.primary, r: 6 }}
            >
              <ErrorBar
                dataKey="error"
                width={4}
                stroke={chartTheme.muted}
                direction="y"
              />
            </Line>
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
