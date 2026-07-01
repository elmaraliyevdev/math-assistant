import { Link } from '@tanstack/react-router'
import { ArrowRight, Sparkles } from 'lucide-react'

import { StatusBadge, toneForProjectStatus } from '@/components/design-system'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import type { useWorkspaceData } from '@/features/workspace/hooks/use-workspace-data'
import { formatRelativeTime } from '@/lib/format-relative-time'
import { formatPercent } from '@/lib/utils'

export function ContinueWorkingCard({
  loading,
  hasGames,
  meta,
}: {
  loading: boolean
  hasGames: boolean
  meta: ReturnType<typeof useWorkspaceData>['continueMeta']
}) {
  if (loading) {
    return (
      <Card className="shadow-none">
        <CardContent className="p-6">
          <Skeleton className="mb-4 h-6 w-48" />
          <Skeleton className="h-10 w-64" />
          <Skeleton className="mt-6 h-10 w-32" />
        </CardContent>
      </Card>
    )
  }

  if (!hasGames || !meta) {
    return (
      <Card className="border-primary/20 shadow-none">
        <CardContent className="p-6 md:p-8">
          <p className="text-sm text-muted-foreground">Get started</p>
          <h3 className="mt-2 text-2xl font-semibold tracking-tight">Create your first game</h3>
          <p className="mt-2 max-w-lg text-sm text-muted-foreground">
            Start designing reel strips, set mathematical goals, and run your first simulation.
          </p>
          <Button className="mt-6" asChild>
            <Link to="/games/create">
              <Sparkles className="h-4 w-4" />
              Create game
            </Link>
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="shadow-none">
      <CardContent className="p-6 md:p-8">
        <p className="text-sm text-muted-foreground">Continue working</p>
        <div className="mt-4 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="min-w-0 space-y-4">
            <div>
              <h3 className="text-2xl font-semibold tracking-tight">{meta.gameName}</h3>
              <p className="mt-1 text-sm text-muted-foreground">Version {meta.versionNumber}</p>
            </div>
            <div className="flex flex-wrap gap-8">
              <div>
                <p className="text-sm text-muted-foreground">Last edited</p>
                <p className="font-medium">{formatRelativeTime(meta.lastEditedAt)}</p>
              </div>
              {meta.designHealth != null ? (
                <div>
                  <p className="text-sm text-muted-foreground">Design health</p>
                  <p className="text-2xl font-semibold tabular-nums">{meta.designHealth}</p>
                </div>
              ) : null}
              {meta.lastSimulationRtp != null ? (
                <div>
                  <p className="text-sm text-muted-foreground">Last simulation</p>
                  <p className="text-2xl font-semibold tabular-nums">
                    {formatPercent(meta.lastSimulationRtp)}
                  </p>
                </div>
              ) : null}
              <div>
                <p className="text-sm text-muted-foreground">Status</p>
                <StatusBadge
                  label={meta.statusLabel}
                  tone={toneForProjectStatus(meta.projectStatus)}
                />
              </div>
            </div>
          </div>
          <Button size="lg" className="shrink-0" asChild>
            <Link
              to="/games/$gameId/versions/$versionId/reel-studio"
              params={{ gameId: meta.gameId, versionId: meta.versionId }}
            >
              Open Studio
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
