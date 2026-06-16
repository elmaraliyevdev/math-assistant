import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { chartTheme } from '@/features/simulations/utils/chart-theme'
import type { SimulationResults } from '@/types/api'
import { formatPercent } from '@/lib/utils'

const SEGMENT_COLORS = [
  'var(--chart-1)',
  'var(--chart-2)',
  'var(--chart-3)',
  'var(--chart-4)',
]

interface RtpDecompositionPieChartProps {
  chart: SimulationResults['rtpDecompositionChart']
}

export function RtpDecompositionPieChart({ chart }: RtpDecompositionPieChartProps) {
  const data = [
    { name: 'Base', value: chart.BASE },
    { name: 'Free Spins', value: chart.FREE_SPINS },
    { name: 'Hold & Win', value: chart.HOLD_AND_WIN },
    { name: 'Jackpot', value: chart.JACKPOT },
  ].filter((item) => item.value > 0)

  if (data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>RTP decomposition</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            No RTP category wins recorded for this simulation.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>RTP decomposition</CardTitle>
        <p className="text-sm text-muted-foreground">
          Total RTP: {chart.totalRtp.toFixed(2)}%
        </p>
      </CardHeader>
      <CardContent className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius={50}
              outerRadius={90}
              paddingAngle={2}
            >
              {data.map((entry, index) => (
                <Cell
                  key={entry.name}
                  fill={SEGMENT_COLORS[index % SEGMENT_COLORS.length]}
                />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: chartTheme.card,
                borderColor: chartTheme.border,
                color: chartTheme.foreground,
              }}
              formatter={(value: number, name: string) => [
                `${value.toFixed(2)}%`,
                name,
              ]}
            />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

interface RtpTargetGaugeProps {
  validation: NonNullable<SimulationResults['rtpValidation']>
}

export function RtpTargetGauge({ validation }: RtpTargetGaugeProps) {
  const min = Math.max(0, validation.targetRtp - 10)
  const max = validation.targetRtp + 10
  const range = max - min
  const actualPosition = ((validation.actualRtp - min) / range) * 100
  const targetPosition = ((validation.targetRtp - min) / range) * 100
  const lowerBound = validation.targetRtp - validation.tolerance
  const upperBound = validation.targetRtp + validation.tolerance
  const bandLeft = ((lowerBound - min) / range) * 100
  const bandWidth = ((upperBound - lowerBound) / range) * 100

  return (
    <Card>
      <CardHeader>
        <CardTitle>Target vs actual RTP</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="relative h-8 rounded-full bg-muted">
          <div
            className="absolute top-1 bottom-1 rounded-full bg-primary/20"
            style={{ left: `${bandLeft}%`, width: `${bandWidth}%` }}
          />
          <div
            className="absolute top-0 h-full w-0.5 bg-primary"
            style={{ left: `${targetPosition}%` }}
            title={`Target ${validation.targetRtp.toFixed(2)}%`}
          />
          <div
            className="absolute top-1/2 h-4 w-4 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-background bg-foreground"
            style={{ left: `${Math.min(100, Math.max(0, actualPosition))}%` }}
            title={`Actual ${validation.actualRtp.toFixed(2)}%`}
          />
        </div>
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>{min.toFixed(1)}%</span>
          <span>
            Target {validation.targetRtp.toFixed(2)}% · Actual{' '}
            {formatPercent(validation.actualRtp / 100, 2)}
          </span>
          <span>{max.toFixed(1)}%</span>
        </div>
      </CardContent>
    </Card>
  )
}
