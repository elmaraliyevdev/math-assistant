import { Link } from '@tanstack/react-router'
import { ArrowRight, FlaskConical } from 'lucide-react'

import { EmptyState } from '@/components/design-system'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { WorkspacePanel } from '@/features/workspace/components/WorkspacePanel'
import type { DashboardSimulationSummary } from '@/services/dashboard'
import { cn } from '@/lib/utils'
import { formatPercent } from '@/lib/utils'

function simulationStatusLabel(status: string): string {
  if (status === 'completed') return 'Completed'
  if (status === 'running') return 'Running'
  if (status === 'pending') return 'Queued'
  if (status === 'failed') return 'Failed'
  return status.replaceAll('_', ' ')
}

function statusTone(status: string): string {
  if (status === 'completed') return 'text-emerald-600 dark:text-emerald-400'
  if (status === 'failed') return 'text-red-600 dark:text-red-400'
  if (status === 'running' || status === 'pending') return 'text-amber-600 dark:text-amber-400'
  return 'text-muted-foreground'
}

export function RecentSimulationsList({
  loading,
  simulations,
}: {
  loading: boolean
  simulations: DashboardSimulationSummary[]
}) {
  if (loading) {
    return (
      <WorkspacePanel title="Recent simulations">
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, index) => (
            <Skeleton key={index} className="h-12 w-full" />
          ))}
        </div>
      </WorkspacePanel>
    )
  }

  if (!simulations.length) {
    return (
      <EmptyState
        icon={FlaskConical}
        title="No simulations yet"
        description="Run your first simulation to validate RTP and volatility."
        action={
          <Button asChild>
            <Link to="/simulations/create">Start simulation</Link>
          </Button>
        }
      />
    )
  }

  return (
    <WorkspacePanel
      title="Recent simulations"
      action={
        <Button variant="ghost" size="sm" className="h-8 text-xs" asChild>
          <Link to="/simulations">View all</Link>
        </Button>
      }
    >
      <ul className="divide-y divide-border">
        {simulations.map((item) => {
          const title = item.gameName
            ? `${item.gameName} ${item.gameVersionLabel ?? ''}`.trim()
            : 'Simulation'
          return (
            <li key={item.simulationId}>
              <Link
                to="/simulations/$simulationId"
                params={{ simulationId: item.simulationId }}
                className="flex items-center justify-between gap-4 py-4 transition-colors hover:bg-muted/50"
              >
                <div className="flex min-w-0 items-center gap-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-muted">
                    <FlaskConical className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div className="min-w-0">
                    <p className="truncate font-medium">{title}</p>
                    <p className="text-xs text-muted-foreground">
                      {item.spinCount.toLocaleString()} spins
                      {item.rtp != null ? ` · ${formatPercent(item.rtp)}` : ''}
                    </p>
                  </div>
                </div>
                <div className="flex shrink-0 items-center gap-3 text-sm">
                  <span className={cn('capitalize', statusTone(item.status))}>
                    {simulationStatusLabel(item.status)}
                  </span>
                  <span className="inline-flex items-center gap-1 text-muted-foreground">
                    View report
                    <ArrowRight className="h-3.5 w-3.5" />
                  </span>
                </div>
              </Link>
            </li>
          )
        })}
      </ul>
    </WorkspacePanel>
  )
}
