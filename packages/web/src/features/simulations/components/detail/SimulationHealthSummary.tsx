import { InfoGrid, MetricCard } from '@/components/design-system/metric-card'
import { cn, formatPercent } from '@/lib/utils'
import { computeSimulationHealth } from '@/features/simulations/utils/health-score'
import type { SimulationResults } from '@/types/api'

export function SimulationHealthSummary({
  results,
}: {
  results: SimulationResults
}) {
  const health = computeSimulationHealth(results)
  const validation = results.rtpValidation

  return (
    <section className="rounded-xl border border-border/40 bg-card/40 p-6">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-sm text-muted-foreground">Simulation health</p>
          <div className="mt-2 flex items-end gap-3">
            <span className="text-5xl font-semibold tabular-nums tracking-tight">
              {health.score}
            </span>
            <span
              className={cn(
                'mb-2 text-sm font-medium',
                health.tone === 'success' && 'text-emerald-600 dark:text-emerald-400',
                health.tone === 'warning' && 'text-amber-600 dark:text-amber-400',
                health.tone === 'destructive' && 'text-destructive',
              )}
            >
              {health.label}
            </span>
          </div>
        </div>
        <InfoGrid className="flex-1 lg:max-w-3xl">
          <MetricCard
            label="RTP"
            value={formatPercent(results.summary.rtp)}
            hint={
              validation
                ? `${validation.difference >= 0 ? '+' : ''}${formatPercent(validation.difference)} vs target`
                : undefined
            }
          />
          <MetricCard
            label="Volatility"
            value={results.summary.volatility.toFixed(3)}
          />
          <MetricCard
            label="Hit rate"
            value={formatPercent(results.summary.hitFrequency)}
          />
          <MetricCard
            label="Confidence"
            value={formatPercent(results.confidenceInterval.confidenceLevel, 0)}
            hint={`CI ${formatPercent(results.confidenceInterval.lowerBound)} – ${formatPercent(results.confidenceInterval.upperBound)}`}
          />
        </InfoGrid>
      </div>
    </section>
  )
}
