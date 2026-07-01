import { Skeleton } from '@/components/ui/skeleton'
import { MetricCard } from '@/components/design-system'

export function SimulationListStats({
  completed,
  running,
  failed,
  avgRtp,
  avgDuration,
  loading,
}: {
  completed: number
  running: number
  failed: number
  avgRtp: string
  avgDuration: string
  loading?: boolean
}) {
  if (loading) {
    return (
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {Array.from({ length: 5 }).map((_, index) => (
          <Skeleton key={index} className="h-[88px] rounded-xl" />
        ))}
      </div>
    )
  }

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
      <MetricCard label="Completed" value={completed.toLocaleString()} />
      <MetricCard label="Running" value={running.toLocaleString()} />
      <MetricCard label="Failed" value={failed.toLocaleString()} />
      <MetricCard label="Average RTP" value={avgRtp} />
      <MetricCard label="Average duration" value={avgDuration} />
    </div>
  )
}
