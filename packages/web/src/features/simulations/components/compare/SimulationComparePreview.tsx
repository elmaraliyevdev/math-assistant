import { Skeleton } from '@/components/ui/skeleton'
import { buildComparePreviewMetrics } from '@/features/simulations/components/compare/compare-preview'
import type { SimulationCompareResponse } from '@/types/api'

export function SimulationComparePreview({
  data,
  loading,
}: {
  data?: SimulationCompareResponse
  loading?: boolean
}) {
  if (loading) {
    return (
      <div className="space-y-3 rounded-xl border border-border/40 p-6">
        <Skeleton className="h-6 w-40" />
        <Skeleton className="h-32 w-full" />
      </div>
    )
  }

  if (!data || data.simulations.length < 2) {
    return (
      <div className="flex h-full min-h-[20rem] items-center justify-center rounded-xl border border-dashed border-border/60 p-8 text-center">
        <div>
          <p className="font-medium">Comparison preview</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Select two or more completed simulations to see RTP, volatility, and hit
            rate deltas instantly.
          </p>
        </div>
      </div>
    )
  }

  const metrics = buildComparePreviewMetrics(data)

  return (
    <div className="space-y-6 rounded-xl border border-border/40 bg-card/30 p-6">
      <div>
        <h2 className="text-lg font-medium">Comparison preview</h2>
        <p className="text-sm text-muted-foreground">
          Live deltas against the first selected simulation.
        </p>
      </div>
      <div className="space-y-4">
        {metrics.map((metric) => (
          <div key={metric.label} className="rounded-lg border border-border/40 p-4">
            <p className="text-sm font-medium text-muted-foreground">{metric.label}</p>
            <div className="mt-3 space-y-2">
              {metric.values.map((entry) => {
                const delta = metric.deltas?.find((item) => item.id === entry.id)
                return (
                  <div
                    key={entry.id}
                    className="flex items-center justify-between gap-4 text-sm"
                  >
                    <span className="truncate text-muted-foreground">{entry.label}</span>
                    <div className="flex items-center gap-3">
                      <span className="font-medium tabular-nums">{entry.value}</span>
                      {delta ? (
                        <span className="text-xs tabular-nums text-muted-foreground">
                          Δ {delta.delta}
                        </span>
                      ) : (
                        <span className="text-xs text-muted-foreground">baseline</span>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
