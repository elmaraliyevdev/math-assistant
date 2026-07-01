import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  ExposureDashboard,
  MetricsCards,
  RTPDashboard,
  VolatilityDashboard,
} from '@/features/simulations/components'
import { formatNumber, formatPercent } from '@/lib/utils'
import type { SimulationResults } from '@/types/api'

export function SimulationMetricsTabs({
  results,
  spinCount,
}: {
  results: SimulationResults
  spinCount: number
}) {
  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-lg font-medium">Metrics</h2>
        <p className="text-sm text-muted-foreground">
          Explore detailed mathematics by category.
        </p>
      </div>
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="flex h-auto flex-wrap justify-start gap-1 bg-transparent p-0">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="rtp">RTP</TabsTrigger>
          <TabsTrigger value="volatility">Volatility</TabsTrigger>
          <TabsTrigger value="confidence">Confidence</TabsTrigger>
          <TabsTrigger value="features">Features</TabsTrigger>
          <TabsTrigger value="raw">Raw data</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <MetricsCards
            title="Summary"
            metrics={[
              { label: 'RTP', value: formatPercent(results.summary.rtp) },
              {
                label: 'Hit rate',
                value: formatPercent(results.summary.hitFrequency),
              },
              {
                label: 'Volatility',
                value: results.summary.volatility.toFixed(3),
              },
              {
                label: 'Total bet',
                value: formatNumber(results.totals.totalBetMinorUnits),
              },
            ]}
          />
          <ExposureDashboard results={results} />
        </TabsContent>

        <TabsContent value="rtp">
          <RTPDashboard results={results} />
        </TabsContent>

        <TabsContent value="volatility">
          <VolatilityDashboard results={results} spinCount={spinCount} />
        </TabsContent>

        <TabsContent value="confidence">
          <MetricsCards
            title="Confidence interval"
            metrics={[
              {
                label: 'RTP estimate',
                value: formatPercent(results.confidenceInterval.rtp),
              },
              {
                label: 'Lower bound',
                value: formatPercent(results.confidenceInterval.lowerBound),
              },
              {
                label: 'Upper bound',
                value: formatPercent(results.confidenceInterval.upperBound),
              },
              {
                label: 'Confidence level',
                value: formatPercent(results.confidenceInterval.confidenceLevel, 0),
              },
            ]}
          />
        </TabsContent>

        <TabsContent value="features" className="space-y-4">
          <FeatureMetricsTable features={results.featureFrequencies} />
          <JackpotMetricsTable jackpots={results.jackpotFrequencies} />
        </TabsContent>

        <TabsContent value="raw">
          <pre className="max-h-[28rem] overflow-auto rounded-xl border border-border/40 bg-muted/20 p-4 text-xs">
            {JSON.stringify(results, null, 2)}
          </pre>
        </TabsContent>
      </Tabs>
    </section>
  )
}

function FeatureMetricsTable({
  features,
}: {
  features: SimulationResults['featureFrequencies']
}) {
  if (features.length === 0) {
    return <p className="text-sm text-muted-foreground">No feature metrics.</p>
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-border/40">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border/40 text-left text-muted-foreground">
            <th className="px-4 py-3 font-medium">Feature</th>
            <th className="px-4 py-3 font-medium">Triggers</th>
            <th className="px-4 py-3 font-medium">Frequency</th>
            <th className="px-4 py-3 font-medium">One in X</th>
          </tr>
        </thead>
        <tbody>
          {features.map((feature) => (
            <tr key={feature.featureName} className="border-b border-border/40 last:border-0">
              <td className="px-4 py-3">{feature.featureName}</td>
              <td className="px-4 py-3 tabular-nums">{formatNumber(feature.triggerCount)}</td>
              <td className="px-4 py-3 tabular-nums">{formatPercent(feature.frequency)}</td>
              <td className="px-4 py-3 tabular-nums">
                {feature.oneInX != null ? feature.oneInX.toFixed(1) : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function JackpotMetricsTable({
  jackpots,
}: {
  jackpots: SimulationResults['jackpotFrequencies']
}) {
  if (jackpots.length === 0) return null

  return (
    <div className="overflow-x-auto rounded-xl border border-border/40">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border/40 text-left text-muted-foreground">
            <th className="px-4 py-3 font-medium">Tier</th>
            <th className="px-4 py-3 font-medium">Hits</th>
            <th className="px-4 py-3 font-medium">Frequency</th>
            <th className="px-4 py-3 font-medium">One in X</th>
          </tr>
        </thead>
        <tbody>
          {jackpots.map((jackpot) => (
            <tr key={jackpot.jackpotTier} className="border-b border-border/40 last:border-0">
              <td className="px-4 py-3">{jackpot.jackpotTier}</td>
              <td className="px-4 py-3 tabular-nums">{formatNumber(jackpot.triggerCount)}</td>
              <td className="px-4 py-3 tabular-nums">{formatPercent(jackpot.frequency)}</td>
              <td className="px-4 py-3 tabular-nums">
                {jackpot.oneInX != null ? jackpot.oneInX.toFixed(1) : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
