import { Link } from '@tanstack/react-router'
import { ChevronDown, Code2, FlaskConical, Film } from 'lucide-react'
import { useState } from 'react'

import { ActionBar } from '@/components/design-system/page-layout'
import { StatusBadge, toneForProjectStatus } from '@/components/design-system/status-badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { CopyHashButton } from '@/features/games/components/GameTable'
import { VERSION_STATUS_LABELS, type VersionDisplayStatus } from '@/features/games/lib/game-status'
import type { GameVersionSummary } from '@/types/api'
import { formatRelativeTime } from '@/lib/format-relative-time'
import { cn } from '@/lib/utils'

export function VersionCard({
  gameId,
  version,
  status,
  health,
  rtp,
  simulationStatus,
  isLatest,
  onViewJson,
}: {
  gameId: string
  version: GameVersionSummary
  status: VersionDisplayStatus
  health: number | null
  rtp: number | null
  simulationStatus: string | null
  isLatest: boolean
  onViewJson: () => void
}) {
  const [advancedOpen, setAdvancedOpen] = useState(false)

  return (
    <Card className={cn('shadow-none', isLatest && 'border-primary/40')}>
      <CardHeader className="flex flex-row items-start justify-between gap-4 space-y-0 pb-4">
        <div className="space-y-2">
          <CardTitle className="text-lg font-medium">Version {version.version}</CardTitle>
          <StatusBadge
            label={VERSION_STATUS_LABELS[status]}
            tone={toneForProjectStatus(status === 'archived' ? 'draft' : status)}
          />
        </div>
        {isLatest ? (
          <span className="text-xs font-medium text-primary">Latest</span>
        ) : null}
      </CardHeader>
      <CardContent className="space-y-4">
        <dl className="grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-3">
          <div>
            <dt className="text-muted-foreground">Updated</dt>
            <dd className="font-medium">{formatRelativeTime(version.createdAt)}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Engine</dt>
            <dd className="font-medium">
              {version.engineVersion.replace('runtime-core@', '')}
            </dd>
          </div>
          {health != null ? (
            <div>
              <dt className="text-muted-foreground">Health</dt>
              <dd className="font-medium tabular-nums">{health}</dd>
            </div>
          ) : null}
          {rtp != null ? (
            <div>
              <dt className="text-muted-foreground">RTP</dt>
              <dd className="font-medium tabular-nums">{(rtp * 100).toFixed(1)}%</dd>
            </div>
          ) : null}
          <div>
            <dt className="text-muted-foreground">Simulation</dt>
            <dd className="font-medium capitalize">
              {simulationStatus ?? 'None'}
            </dd>
          </div>
        </dl>

        <button
          type="button"
          className="inline-flex items-center gap-1 text-xs text-muted-foreground transition-colors hover:text-foreground"
          onClick={() => setAdvancedOpen((open) => !open)}
        >
          Advanced
          <ChevronDown
            className={cn('h-3.5 w-3.5 transition-transform', advancedOpen && 'rotate-180')}
          />
        </button>
        {advancedOpen ? (
          <div className="space-y-3 rounded-lg border border-border bg-muted/30 p-4 text-xs">
            <div>
              <p className="text-muted-foreground">Content hash</p>
              <p className="mt-1 break-all font-mono">{version.contentHash}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Runtime version</p>
              <p className="mt-1">{version.engineVersion}</p>
            </div>
            <CopyHashButton hash={version.contentHash} />
          </div>
        ) : null}
      </CardContent>
      <CardFooter className="border-t border-border pt-6">
        <ActionBar>
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
          <Button variant="outline" size="sm" onClick={onViewJson}>
            <Code2 className="h-4 w-4" />
            JSON
          </Button>
        </ActionBar>
      </CardFooter>
    </Card>
  )
}
