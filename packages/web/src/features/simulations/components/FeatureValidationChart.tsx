import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { chartMargin, chartTheme } from '@/features/simulations/utils/chart-theme'
import type { SimulationResults } from '@/types/api'
import { formatPercent } from '@/lib/utils'

interface FeatureValidationChartProps {
  items: SimulationResults['featureValidation']
}

export function FeatureValidationChart({ items }: FeatureValidationChartProps) {
  const data = items.map((item) => ({
    name: item.feature.replace(/_/g, ' '),
    observed: item.observedFrequency,
    expected: item.expectedFrequency,
    status: item.status,
  }))

  if (data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Feature frequency validation</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            No feature validation data available.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Feature frequency validation</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="h-72">
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
                formatter={(value: number, name: string) => [
                  formatPercent(value),
                  name === 'observed' ? 'Observed' : 'Expected',
                ]}
              />
              <Legend />
              <Bar
                dataKey="observed"
                name="Observed"
                fill={chartTheme.primary}
                radius={[4, 4, 0, 0]}
              />
              <Bar
                dataKey="expected"
                name="Expected"
                fill="var(--chart-2)"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="flex flex-wrap gap-2">
          {items.map((item) => (
            <Badge
              key={item.feature}
              variant={item.status === 'PASS' ? 'success' : 'danger'}
            >
              {item.feature}: {item.status}
            </Badge>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
