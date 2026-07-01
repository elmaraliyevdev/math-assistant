import { Link } from '@tanstack/react-router'
import type { ReactNode } from 'react'
import { ChevronRight } from 'lucide-react'

import { ProjectStatusBadge } from '@/features/workspace/components/WorkspacePanel'
import type { ProjectStatus } from '@/features/workspace/lib/workspace-status'
import { formatRelativeTime } from '@/lib/format-relative-time'
import { cn, formatPercent } from '@/lib/utils'

function formatShortDate(value: string): string {
  return new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric' }).format(
    new Date(value),
  )
}

export function GameBreadcrumb({ gameName }: { gameName: string }) {
  return (
    <nav aria-label="Breadcrumb" className="text-sm text-muted-foreground">
      <ol className="flex items-center gap-1.5">
        <li>
          <Link to="/games" className="transition-colors hover:text-foreground">
            Games
          </Link>
        </li>
        <ChevronRight className="h-3.5 w-3.5 opacity-50" />
        <li className="font-medium text-foreground">{gameName}</li>
      </ol>
    </nav>
  )
}

export function GameHero({
  name,
  description,
  status,
  statusLabel,
  createdAt,
  updatedAt,
  engineVersion,
  designHealth,
  versionCount,
  lastRtp,
  lastSimulationAt,
  actions,
}: {
  name: string
  description: string | null
  status: ProjectStatus
  statusLabel: string
  createdAt: string
  updatedAt: string
  engineVersion: string | null
  designHealth: number | null
  versionCount: number
  lastRtp: number | null
  lastSimulationAt: string | null
  actions: ReactNode
}) {
  return (
    <section className="rounded-xl border border-border bg-card p-6 md:p-8">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0 space-y-4">
          <GameBreadcrumb gameName={name} />
          <div>
            <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">{name}</h1>
            <p className="mt-2 max-w-2xl text-muted-foreground">
              {description || 'Slot game project'}
            </p>
          </div>
          <ProjectStatusBadge label={statusLabel} status={status} />
          <p className="text-sm text-muted-foreground">
            Updated {formatRelativeTime(updatedAt)}
          </p>
          <div className="flex flex-wrap gap-6 text-sm">
            {designHealth != null ? (
              <div>
                <p className="text-xs text-muted-foreground">Design health</p>
                <p className="text-2xl font-semibold tabular-nums">{designHealth}</p>
              </div>
            ) : null}
            <div>
              <p className="text-xs text-muted-foreground">Versions</p>
              <p className="text-2xl font-semibold tabular-nums">{versionCount}</p>
            </div>
            {lastRtp != null ? (
              <div>
                <p className="text-xs text-muted-foreground">Last RTP</p>
                <p className="text-2xl font-semibold tabular-nums">{formatPercent(lastRtp)}</p>
              </div>
            ) : null}
            {lastSimulationAt ? (
              <div>
                <p className="text-xs text-muted-foreground">Last simulation</p>
                <p className="font-medium">{formatRelativeTime(lastSimulationAt)}</p>
              </div>
            ) : null}
          </div>
          <p className="text-xs text-muted-foreground">
            Created {formatShortDate(createdAt)}
            {engineVersion ? (
              <>
                {' '}
                · Engine {engineVersion.replace('runtime-core@', 'runtime-core ')}
              </>
            ) : null}
          </p>
        </div>
        <div className="flex shrink-0 flex-wrap gap-2">{actions}</div>
      </div>
    </section>
  )
}

export function GamePageTabs() {
  const tabs = [
    { id: 'overview', label: 'Overview', active: true },
    { id: 'versions', label: 'Versions', active: false },
    { id: 'simulations', label: 'Simulations', active: false },
    { id: 'certification', label: 'Certification', active: false },
    { id: 'analytics', label: 'Analytics', active: false },
  ]

  return (
    <div className="flex gap-1 overflow-x-auto border-b border-border/40">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          disabled={!tab.active}
          className={cn(
            'shrink-0 border-b-2 px-4 py-2.5 text-sm font-medium transition-colors',
            tab.active
              ? 'border-primary text-foreground'
              : 'border-transparent text-muted-foreground opacity-50',
          )}
        >
          {tab.label}
        </button>
      ))}
    </div>
  )
}
