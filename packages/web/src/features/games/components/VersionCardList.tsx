import { Link } from '@tanstack/react-router'
import { ArrowRight, ChevronDown, Code2, FlaskConical, Film } from 'lucide-react'
import { useState } from 'react'

import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { CopyHashButton } from '@/features/games/components/GameTable'
import type { DashboardSimulationSummary } from '@/services/dashboard'
import {
  deriveVersionStatus,
  VERSION_STATUS_LABELS,
  VERSION_STATUS_STYLES,
  versionDesignHealth,
  type VersionDisplayStatus,
} from '@/features/games/lib/game-status'
import { getLatestVersion } from '@/features/workspace/lib/workspace-status'
import type { GameVersionSummary } from '@/types/api'
import { formatRelativeTime } from '@/lib/format-relative-time'
import { cn } from '@/lib/utils'

function VersionStatusBadge({
  status,
}: {
  status: VersionDisplayStatus
}) {
  return (
    <span
      className={cn(
        'inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium',
        VERSION_STATUS_STYLES[status],
      )}
    >
      {VERSION_STATUS_LABELS[status]}
    </span>
  )
}

function VersionCard({
  gameId,
  version,
  latestVersion,
  simulation,
  onViewJson,
}: {
  gameId: string
  version: GameVersionSummary
  latestVersion: GameVersionSummary | null
  simulation: DashboardSimulationSummary | null
  onViewJson: (version: GameVersionSummary) => void
}) {
  const [advancedOpen, setAdvancedOpen] = useState(false)
  const status = deriveVersionStatus(version, latestVersion, simulation)
  const health = versionDesignHealth(status, simulation)
  const isLatest = latestVersion?.id === version.id

  return (
    <article
      className={cn(
        'rounded-2xl bg-muted/15 p-5 ring-1 ring-border/40 transition-colors',
        isLatest && 'ring-primary/25 bg-primary/5',
      )}
    >
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0 space-y-3">
          <div className="flex flex-wrap items-center gap-3">
            <h3 className="text-lg font-semibold">Version {version.version}</h3>
            <VersionStatusBadge status={status} />
          </div>
          <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
            <span>Updated {formatRelativeTime(version.createdAt)}</span>
            <span>Engine {version.engineVersion.replace('runtime-core@', '')}</span>
            {health != null ? <span>Health {health}</span> : null}
            {simulation?.rtp != null ? (
              <span>RTP {(simulation.rtp * 100).toFixed(1)}%</span>
            ) : null}
            {simulation ? (
              <span className="capitalize">Simulation {simulation.status}</span>
            ) : (
              <span>No simulation yet</span>
            )}
          </div>
          <button
            type="button"
            className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
            onClick={() => setAdvancedOpen((open) => !open)}
          >
            Advanced
            <ChevronDown
              className={cn('h-3.5 w-3.5 transition-transform', advancedOpen && 'rotate-180')}
            />
          </button>
          {advancedOpen ? (
            <div className="space-y-2 rounded-xl bg-background/60 p-3 text-xs ring-1 ring-border/30">
              <div>
                <p className="text-muted-foreground">Content hash</p>
                <p className="mt-0.5 break-all font-mono">{version.contentHash}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Runtime version</p>
                <p className="mt-0.5">{version.engineVersion}</p>
              </div>
              <CopyHashButton hash={version.contentHash} />
            </div>
          ) : null}
        </div>
        <div className="flex flex-wrap gap-2">
          <Button asChild>
            <Link
              to="/games/$gameId/versions/$versionId/reel-studio"
              params={{ gameId, versionId: version.id }}
            >
              <Film className="h-4 w-4" />
              {isLatest ? 'Continue' : 'Open Studio'}
            </Link>
          </Button>
          <Button variant="secondary" asChild>
            <Link to="/simulations/create" search={{ gameVersionId: version.id }}>
              <FlaskConical className="h-4 w-4" />
              Simulation
            </Link>
          </Button>
          <Button variant="outline" size="sm" onClick={() => onViewJson(version)}>
            <Code2 className="h-4 w-4" />
            JSON
          </Button>
        </div>
      </div>
    </article>
  )
}

export function VersionCardList({
  gameId,
  versions,
  simulations,
  loading,
  onViewJson,
  onCreateVersion,
}: {
  gameId: string
  versions: GameVersionSummary[]
  simulations: DashboardSimulationSummary[]
  loading?: boolean
  onViewJson: (version: GameVersionSummary) => void
  onCreateVersion: () => void
}) {
  if (loading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, index) => (
          <Skeleton key={index} className="h-32 w-full rounded-2xl" />
        ))}
      </div>
    )
  }

  if (!versions.length) {
    return (
      <div className="rounded-2xl border border-dashed border-border/60 py-12 text-center">
        <p className="font-medium">No versions yet</p>
        <p className="mt-2 text-sm text-muted-foreground">
          Create a version to start designing in the Mathematical Design Studio.
        </p>
        <Button className="mt-4" onClick={onCreateVersion}>
          New version
        </Button>
      </div>
    )
  }

  const latestVersion = getLatestVersion(versions)
  const simByVersion = new Map(simulations.map((item) => [item.gameVersionId, item]))
  const sorted = [...versions].sort((a, b) => b.version - a.version)

  return (
    <div className="space-y-3">
      {sorted.map((version) => (
        <VersionCard
          key={version.id}
          gameId={gameId}
          version={version}
          latestVersion={latestVersion}
          simulation={simByVersion.get(version.id) ?? null}
          onViewJson={onViewJson}
        />
      ))}
    </div>
  )
}

export function VersionHistoryHeader({ onCreateVersion }: { onCreateVersion: () => void }) {
  return (
    <div className="mb-4 flex items-center justify-between gap-4">
      <div>
        <h2 className="text-lg font-semibold">Version history</h2>
        <p className="text-sm text-muted-foreground">
          Continue designing or validate with simulation
        </p>
      </div>
      <Button variant="ghost" size="sm" className="gap-1 text-primary" onClick={onCreateVersion}>
        New version
        <ArrowRight className="h-3.5 w-3.5" />
      </Button>
    </div>
  )
}
