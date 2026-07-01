import { Link } from '@tanstack/react-router'
import { ArrowRight } from 'lucide-react'

import { EmptyState } from '@/components/design-system'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
  ProjectStatusBadge,
  WorkspacePanel,
} from '@/features/workspace/components/WorkspacePanel'
import type { WorkspaceProject } from '@/features/workspace/hooks/use-workspace-data'

export function RecentProjectsList({
  loading,
  projects,
}: {
  loading: boolean
  projects: WorkspaceProject[]
}) {
  if (loading) {
    return (
      <WorkspacePanel title="Recent projects">
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, index) => (
            <Skeleton key={index} className="h-14 w-full" />
          ))}
        </div>
      </WorkspacePanel>
    )
  }

  if (!projects.length) {
    return (
      <EmptyState
        title="No projects yet"
        description="Create a game to start designing reel strips."
        action={
          <Button asChild>
            <Link to="/games/create">Create game</Link>
          </Button>
        }
      />
    )
  }

  return (
    <WorkspacePanel
      title="Recent projects"
      action={
        <Button variant="ghost" size="sm" className="h-8 text-xs" asChild>
          <Link to="/games">View all</Link>
        </Button>
      }
    >
      <ul className="divide-y divide-border">
        {projects.map((project) => (
          <li key={project.game.id}>
            <Link
              to={
                project.latestVersion
                  ? '/games/$gameId/versions/$versionId/reel-studio'
                  : '/games/$gameId'
              }
              params={
                project.latestVersion
                  ? { gameId: project.game.id, versionId: project.latestVersion.id }
                  : { gameId: project.game.id }
              }
              className="flex items-center justify-between gap-4 py-4 transition-colors hover:text-primary"
            >
              <div className="min-w-0">
                <p className="truncate font-medium">{project.game.name}</p>
                <div className="mt-1">
                  <ProjectStatusBadge label={project.statusLabel} status={project.status} />
                </div>
              </div>
              <span className="inline-flex shrink-0 items-center gap-1 text-sm text-muted-foreground">
                Continue
                <ArrowRight className="h-3.5 w-3.5" />
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </WorkspacePanel>
  )
}
