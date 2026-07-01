import { Skeleton } from '@/components/ui/skeleton'
import { WorkspacePanel } from '@/features/workspace/components/WorkspacePanel'
import { cn } from '@/lib/utils'

interface HealthRow {
  label: string
  value: number
  tone: 'green' | 'amber' | 'red' | 'neutral'
}

function toneDot(tone: HealthRow['tone']) {
  return cn(
    'h-2 w-2 shrink-0 rounded-full',
    tone === 'green' && 'bg-emerald-500',
    tone === 'amber' && 'bg-amber-500',
    tone === 'red' && 'bg-red-500',
    tone === 'neutral' && 'bg-muted-foreground/40',
  )
}

export function WorkspaceHealthPanel({
  loading,
  health,
}: {
  loading: boolean
  health: {
    games: number
    readyForCertification: number
    runningSimulations: number
    needsAttention: number
    failedJobs: number
  } | null
}) {
  if (loading) {
    return (
      <WorkspacePanel title="Workspace health">
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, index) => (
            <Skeleton key={index} className="h-8 w-full" />
          ))}
        </div>
      </WorkspacePanel>
    )
  }

  if (!health) return null

  const rows: HealthRow[] = [
    { label: 'Games', value: health.games, tone: 'neutral' },
    {
      label: 'Ready for certification',
      value: health.readyForCertification,
      tone: health.readyForCertification > 0 ? 'green' : 'neutral',
    },
    {
      label: 'Running simulations',
      value: health.runningSimulations,
      tone: health.runningSimulations > 0 ? 'amber' : 'neutral',
    },
    {
      label: 'Needs attention',
      value: health.needsAttention,
      tone: health.needsAttention > 0 ? 'amber' : 'green',
    },
    {
      label: 'Failed jobs',
      value: health.failedJobs,
      tone: health.failedJobs > 0 ? 'red' : 'green',
    },
  ]

  return (
    <WorkspacePanel title="Workspace health">
      <ul className="space-y-3">
        {rows.map((row) => (
          <li key={row.label} className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2.5">
              <span className={toneDot(row.tone)} />
              <span className="text-sm text-muted-foreground">{row.label}</span>
            </div>
            <span className="text-sm font-semibold tabular-nums">{row.value}</span>
          </li>
        ))}
      </ul>
    </WorkspacePanel>
  )
}
