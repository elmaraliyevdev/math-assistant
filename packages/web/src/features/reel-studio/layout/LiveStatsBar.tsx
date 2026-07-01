import { useConstraintStudio } from '@/features/reel-studio/constraints/context/constraint-studio-context'
import { useReelStudio } from '@/features/reel-studio/context/reel-studio-context'
import { useGeneratorStudio } from '@/features/reel-studio/generator/context/generator-context'
import { cn, formatPercent } from '@/lib/utils'

function MetricPill({
  label,
  value,
  tone = 'neutral',
}: {
  label: string
  value: string
  tone?: 'good' | 'warn' | 'bad' | 'neutral'
}) {
  return (
    <div className="flex shrink-0 items-center gap-2 rounded-md border border-border/30 bg-background/60 px-2.5 py-1">
      <span className="text-[10px] uppercase tracking-wide text-muted-foreground">{label}</span>
      <span
        className={cn(
          'text-xs font-medium tabular-nums',
          tone === 'good' && 'text-emerald-600 dark:text-emerald-400',
          tone === 'warn' && 'text-amber-600 dark:text-amber-400',
          tone === 'bad' && 'text-red-600 dark:text-red-400',
        )}
      >
        {value}
      </span>
    </div>
  )
}

export function LiveStatsBar() {
  const { stats } = useReelStudio()
  const { validation } = useConstraintStudio()
  const { designHealth } = useGeneratorStudio()

  const wildCount = stats.totals.symbolCounts.find((entry) =>
    entry.symbolId.toLowerCase().includes('wild'),
  )?.count
  const scatterCount = stats.totals.symbolCounts.find((entry) =>
    entry.symbolId.toLowerCase().includes('scatter'),
  )?.count
  const total = stats.totals.totalSymbols || 1
  const errors = validation.summary.error
  const warnings = validation.summary.warning

  const rtpMetric = designHealth.metrics.find((m) => m.id === 'rtp')
  const volatilityMetric = designHealth.metrics.find((m) => m.id === 'volatility')

  return (
    <div className="flex h-9 shrink-0 items-center gap-2 overflow-x-auto border-b border-border/20 bg-muted/5 px-3">
      <MetricPill
        label="Health"
        value={String(designHealth.overallScore)}
        tone={
          designHealth.overallScore >= 80 ? 'good' : designHealth.overallScore >= 60 ? 'warn' : 'bad'
        }
      />
      {rtpMetric ? (
        <MetricPill
          label="RTP"
          value={formatPercent(rtpMetric.score / 100, 1)}
          tone={rtpMetric.status === 'pass' ? 'good' : 'warn'}
        />
      ) : null}
      {volatilityMetric ? (
        <MetricPill label="Volatility" value={String(Math.round(volatilityMetric.score))} />
      ) : null}
      <MetricPill
        label="Hit rate"
        value={total > 0 ? formatPercent(stats.totals.symbolCounts[0]?.percentage ?? 0, 0) : '—'}
      />
      {wildCount != null ? (
        <MetricPill label="Wilds" value={String(wildCount)} />
      ) : null}
      {scatterCount != null ? (
        <MetricPill label="Scatters" value={String(scatterCount)} />
      ) : null}
      <MetricPill
        label="Validation"
        value={errors > 0 ? `${errors} errors` : warnings > 0 ? `${warnings} warnings` : 'Pass'}
        tone={errors > 0 ? 'bad' : warnings > 0 ? 'warn' : 'good'}
      />
    </div>
  )
}
