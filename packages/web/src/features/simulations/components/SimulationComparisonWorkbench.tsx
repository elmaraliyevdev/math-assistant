import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { ReactNode } from 'react'

import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { chartMargin, chartTheme } from '@/features/simulations/utils/chart-theme'
import {
  deriveComparisonHighlights,
  formatDurationMs,
} from '@/features/simulations/utils/workbench'
import type { SimulationCompareResponse } from '@/types/api'
import { formatNumber, formatPercent } from '@/lib/utils'

const SERIES_COLORS = [
  'var(--chart-1)',
  'var(--chart-2)',
  'var(--chart-3)',
  'var(--chart-4)',
  'var(--chart-5)',
]

interface SimulationComparisonWorkbenchProps {
  data: SimulationCompareResponse
}

export function SimulationComparisonWorkbench({
  data,
}: SimulationComparisonWorkbenchProps) {
  const highlights = deriveComparisonHighlights(data)
  const labels = Object.fromEntries(
    data.simulations.map((entry, index) => [
      entry.simulationId,
      entry.gameName && entry.gameVersionLabel
        ? `${entry.gameName} ${entry.gameVersionLabel}`
        : entry.gameName ?? `Run ${index + 1}`,
    ]),
  )

  const rtpChartData = data.comparison.rtp.map((item, index) => ({
    name: labels[item.simulationId] ?? item.simulationId.slice(0, 8),
    rtp: item.value,
    simulationId: item.simulationId,
    color: SERIES_COLORS[index % SERIES_COLORS.length],
  }))

  const volatilityChartData = data.comparison.volatility.map((item, index) => ({
    name: labels[item.simulationId] ?? item.simulationId.slice(0, 8),
    volatility: item.value,
    color: SERIES_COLORS[index % SERIES_COLORS.length],
  }))

  const featureNames = [
    ...new Set(data.comparison.featureFrequency.map((item) => item.featureName)),
  ]
  const featureChartData = featureNames.map((featureName) => {
    const row: Record<string, string | number> = { feature: featureName }
    for (const item of data.comparison.featureFrequency) {
      if (item.featureName === featureName) {
        row[labels[item.simulationId] ?? item.simulationId] = item.frequency
      }
    }
    return row
  })

  const decompositionChartData = data.comparison.rtpDecomposition.map((item) => ({
    name: labels[item.simulationId] ?? item.simulationId.slice(0, 8),
    BASE: item.BASE,
    FREE_SPINS: item.FREE_SPINS,
    HOLD_AND_WIN: item.HOLD_AND_WIN,
    JACKPOT: item.JACKPOT,
  }))

  const evolutionData = data.simulations.map((entry, index) => ({
    name: `Run ${index + 1}`,
    rtpPercent: entry.results.summary.rtp * 100,
    targetRtp: entry.results.rtpValidation?.targetRtp ?? null,
  }))

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap gap-2">
        {highlights.bestRtpMatchId && (
          <Badge variant="success">
            Best RTP match: {labels[highlights.bestRtpMatchId]}
          </Badge>
        )}
        {highlights.lowestVolatilityId && (
          <Badge variant="secondary">
            Lowest volatility: {labels[highlights.lowestVolatilityId]}
          </Badge>
        )}
        {highlights.highestHitFrequencyId && (
          <Badge variant="secondary">
            Highest hit frequency: {labels[highlights.highestHitFrequencyId]}
          </Badge>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Side-by-side metrics</CardTitle>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-muted-foreground">
                <th className="pb-2 pr-4 font-medium">Run</th>
                <th className="pb-2 pr-4 font-medium">RTP</th>
                <th className="pb-2 pr-4 font-medium">RTP vs target</th>
                <th className="pb-2 pr-4 font-medium">Volatility</th>
                <th className="pb-2 pr-4 font-medium">Hit frequency</th>
                <th className="pb-2 pr-4 font-medium">CI</th>
                <th className="pb-2 pr-4 font-medium">Spins</th>
                <th className="pb-2 font-medium">Runtime</th>
              </tr>
            </thead>
            <tbody>
              {data.simulations.map((entry, index) => {
                const ci = data.comparison.confidenceIntervals.find(
                  (item) => item.simulationId === entry.simulationId,
                )
                const validation = entry.results.rtpValidation
                return (
                  <tr key={entry.simulationId} className="border-b last:border-0">
                    <td className="py-2 pr-4 font-medium">Run {index + 1}</td>
                    <td className="py-2 pr-4">{formatPercent(entry.results.summary.rtp)}</td>
                    <td className="py-2 pr-4">
                      {validation
                        ? `${validation.difference >= 0 ? '+' : ''}${validation.difference.toFixed(2)}%`
                        : '—'}
                    </td>
                    <td className="py-2 pr-4">
                      {formatNumber(entry.results.summary.volatility)}
                    </td>
                    <td className="py-2 pr-4">
                      {formatPercent(entry.results.summary.hitFrequency)}
                    </td>
                    <td className="py-2 pr-4">
                      {ci
                        ? `${formatPercent(ci.lowerBound)} – ${formatPercent(ci.upperBound)}`
                        : '—'}
                    </td>
                    <td className="py-2 pr-4">{formatNumber(entry.detail.spinCount)}</td>
                    <td className="py-2">
                      {formatDurationMs(entry.runtimeDurationMs)}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </CardContent>
      </Card>

      <div className="grid gap-6 xl:grid-cols-2">
        <ChartCard title="RTP comparison">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={rtpChartData} margin={chartMargin}>
              <CartesianGrid stroke={chartTheme.border} strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fill: chartTheme.muted, fontSize: 12 }} />
              <YAxis
                tickFormatter={(value) => formatPercent(value, 1)}
                tick={{ fill: chartTheme.muted, fontSize: 12 }}
              />
              <Tooltip formatter={(value: number) => formatPercent(value)} />
              <Bar dataKey="rtp" radius={[4, 4, 0, 0]}>
                {rtpChartData.map((entry) => (
                  <Cell key={entry.simulationId} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Volatility comparison">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={volatilityChartData} margin={chartMargin}>
              <CartesianGrid stroke={chartTheme.border} strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fill: chartTheme.muted, fontSize: 12 }} />
              <YAxis tick={{ fill: chartTheme.muted, fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="volatility" radius={[4, 4, 0, 0]}>
                {volatilityChartData.map((entry, index) => (
                  <Cell key={entry.name} fill={SERIES_COLORS[index % SERIES_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Feature frequency comparison">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={featureChartData} margin={chartMargin}>
              <CartesianGrid stroke={chartTheme.border} strokeDasharray="3 3" />
              <XAxis dataKey="feature" tick={{ fill: chartTheme.muted, fontSize: 12 }} />
              <YAxis
                tickFormatter={(value) => formatPercent(value, 1)}
                tick={{ fill: chartTheme.muted, fontSize: 12 }}
              />
              <Tooltip formatter={(value: number) => formatPercent(value)} />
              <Legend />
              {data.simulations.map((entry, index) => (
                <Bar
                  key={entry.simulationId}
                  dataKey={labels[entry.simulationId] ?? entry.simulationId}
                  fill={SERIES_COLORS[index % SERIES_COLORS.length]}
                  radius={[4, 4, 0, 0]}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="RTP decomposition">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={decompositionChartData} margin={chartMargin}>
              <CartesianGrid stroke={chartTheme.border} strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fill: chartTheme.muted, fontSize: 12 }} />
              <YAxis tick={{ fill: chartTheme.muted, fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="BASE" stackId="rtp" fill="var(--chart-1)" />
              <Bar dataKey="FREE_SPINS" stackId="rtp" fill="var(--chart-2)" />
              <Bar dataKey="HOLD_AND_WIN" stackId="rtp" fill="var(--chart-3)" />
              <Bar dataKey="JACKPOT" stackId="rtp" fill="var(--chart-4)" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <ChartCard title="RTP evolution">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={evolutionData} margin={chartMargin}>
            <CartesianGrid stroke={chartTheme.border} strokeDasharray="3 3" />
            <XAxis dataKey="name" tick={{ fill: chartTheme.muted, fontSize: 12 }} />
            <YAxis
              tickFormatter={(value) => `${value.toFixed(1)}%`}
              tick={{ fill: chartTheme.muted, fontSize: 12 }}
            />
            <Tooltip formatter={(value: number) => `${value.toFixed(2)}%`} />
            <Line
              type="monotone"
              dataKey="rtpPercent"
              stroke={chartTheme.primary}
              strokeWidth={2}
              dot={{ r: 4 }}
              name="Actual RTP"
            />
          </LineChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  )
}

function ChartCard({
  title,
  children,
}: {
  title: string
  children: ReactNode
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="h-72">{children}</CardContent>
    </Card>
  )
}
