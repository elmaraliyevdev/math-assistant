import { StatusBadge } from '@/components/design-system'
import { cn, formatPercent } from '@/lib/utils'
import type { SimulationIntelligenceReport, SimulationResults } from '@/types/api'

type ComparisonRow = {
  label: string
  target: string
  observed: string
  difference: string
  status: 'success' | 'warning' | 'destructive'
  statusLabel: string
}

function buildRows(
  results: SimulationResults,
  intelligence?: SimulationIntelligenceReport | null,
): ComparisonRow[] {
  if (intelligence?.designVsReality.length) {
    return intelligence.designVsReality.map((item) => ({
      label: item.label,
      target: item.target,
      observed: item.observed,
      difference: '—',
      status:
        item.status === 'green'
          ? 'success'
          : item.status === 'yellow'
            ? 'warning'
            : 'destructive',
      statusLabel:
        item.status === 'green'
          ? 'On target'
          : item.status === 'yellow'
            ? 'Warning'
            : 'Off target',
    }))
  }

  const rows: ComparisonRow[] = []
  const validation = results.rtpValidation
  if (validation) {
    rows.push({
      label: 'RTP',
      target: formatPercent(validation.targetRtp),
      observed: formatPercent(validation.actualRtp),
      difference: `${validation.difference >= 0 ? '+' : ''}${formatPercent(validation.difference)}`,
      status: validation.withinTolerance ? 'success' : 'warning',
      statusLabel: validation.withinTolerance ? 'On target' : 'Warning',
    })
  }

  for (const item of results.featureValidation) {
    rows.push({
      label: item.feature,
      target: formatPercent(item.expectedFrequency),
      observed: formatPercent(item.observedFrequency),
      difference: `${item.difference >= 0 ? '+' : ''}${formatPercent(item.difference)}`,
      status:
        item.status === 'pass'
          ? 'success'
          : item.status === 'warning'
            ? 'warning'
            : 'destructive',
      statusLabel:
        item.status === 'pass'
          ? 'On target'
          : item.status === 'warning'
            ? 'Warning'
            : 'Off target',
    })
  }

  return rows
}

export function SimulationDesignComparison({
  results,
  intelligence,
}: {
  results: SimulationResults
  intelligence?: SimulationIntelligenceReport | null
}) {
  const rows = buildRows(results, intelligence)
  if (rows.length === 0) return null

  return (
    <section className="space-y-3">
      <div>
        <h2 className="text-lg font-medium">Design vs reality</h2>
        <p className="text-sm text-muted-foreground">
          How observed mathematics compare to design targets.
        </p>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {rows.map((row) => (
          <div
            key={row.label}
            className="rounded-xl border border-border/40 bg-card/30 p-4"
          >
            <div className="flex items-start justify-between gap-2">
              <p className="font-medium">{row.label}</p>
              <StatusBadge label={row.statusLabel} tone={row.status} />
            </div>
            <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <div>
                <dt className="text-muted-foreground">Target</dt>
                <dd className="mt-1 font-medium tabular-nums">{row.target}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Observed</dt>
                <dd className="mt-1 font-medium tabular-nums">{row.observed}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Difference</dt>
                <dd
                  className={cn(
                    'mt-1 font-medium tabular-nums',
                    row.status === 'success' && 'text-emerald-600 dark:text-emerald-400',
                    row.status === 'warning' && 'text-amber-600 dark:text-amber-400',
                    row.status === 'destructive' && 'text-destructive',
                  )}
                >
                  {row.difference}
                </dd>
              </div>
            </dl>
          </div>
        ))}
      </div>
    </section>
  )
}
