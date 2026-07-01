import { Link } from '@tanstack/react-router'
import { Copy, Star } from 'lucide-react'
import { useState } from 'react'

import { StatusBadge, toneForProjectStatus } from '@/components/design-system'
import { Button } from '@/components/ui/button'
import { getPinnedGameIds, togglePinnedGame } from '@/features/reel-studio/lib/studio-pins'
import type { WorkspaceProject } from '@/features/workspace/hooks/use-workspace-data'
import { formatRelativeTime } from '@/lib/format-relative-time'
import { cn } from '@/lib/utils'

export function StudioProjectCard({
  project,
  pinned: pinnedProp,
  onTogglePin,
}: {
  project: WorkspaceProject
  pinned?: boolean
  onTogglePin?: (gameId: string) => void
}) {
  const [pinned, setPinned] = useState(pinnedProp ?? getPinnedGameIds().includes(project.game.id))
  const version = project.latestVersion

  const handlePin = () => {
    const next = togglePinnedGame(project.game.id)
    setPinned(next.includes(project.game.id))
    onTogglePin?.(project.game.id)
  }

  return (
    <div className="group flex items-center gap-3 rounded-lg border border-border/60 bg-card px-3 py-2.5 transition-shadow hover:shadow-sm">
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="h-8 w-8 shrink-0"
        onClick={handlePin}
        aria-label={pinned ? 'Unpin project' : 'Pin project'}
      >
        <Star
          className={cn('h-4 w-4', pinned ? 'fill-amber-400 text-amber-400' : 'text-muted-foreground')}
        />
      </Button>
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium">{project.game.name}</p>
        <p className="text-xs text-muted-foreground">
          {version ? `v${version.version}` : 'No version'} ·{' '}
          {formatRelativeTime(project.game.updatedAt)}
        </p>
      </div>
      <StatusBadge
        label={project.statusLabel}
        tone={toneForProjectStatus(project.status)}
        className="hidden sm:inline-flex"
      />
      <div className="flex shrink-0 gap-1 opacity-100 transition-opacity sm:opacity-0 sm:group-hover:opacity-100">
        {version ? (
          <Button size="sm" asChild>
            <Link
              to="/games/$gameId/versions/$versionId/reel-studio"
              params={{ gameId: project.game.id, versionId: version.id }}
            >
              Open
            </Link>
          </Button>
        ) : (
          <Button size="sm" variant="outline" asChild>
            <Link to="/games/$gameId" params={{ gameId: project.game.id }}>
              View
            </Link>
          </Button>
        )}
        <Button size="icon" variant="ghost" className="h-8 w-8" asChild title="Duplicate">
          <Link to="/games/$gameId" params={{ gameId: project.game.id }}>
            <Copy className="h-3.5 w-3.5" />
          </Link>
        </Button>
      </div>
    </div>
  )
}
