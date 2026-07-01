import { Link } from '@tanstack/react-router'

import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { GameStatusBadge } from '@/features/games/components/GamesToolbar'
import type { GameListItem } from '@/features/games/hooks/use-games-with-status'
import { formatRelativeTime } from '@/lib/format-relative-time'
import { cn } from '@/lib/utils'

export function GameProjectList({
  items,
  loading,
}: {
  items: GameListItem[]
  loading: boolean
}) {
  if (loading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 5 }).map((_, index) => (
          <Skeleton key={index} className="h-16 w-full rounded-xl" />
        ))}
      </div>
    )
  }

  return (
    <Card className="overflow-hidden shadow-none">
      <div className="hidden grid-cols-[minmax(0,2fr)_minmax(0,1.5fr)_auto_auto_auto] gap-4 border-b border-border px-6 py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground md:grid">
        <span>Game</span>
        <span>Description</span>
        <span>Updated</span>
        <span>Versions</span>
        <span>Status</span>
      </div>
      <ul className="divide-y divide-border">
        {items.map((item) => (
          <li key={item.game.id}>
            <Link
              to="/games/$gameId"
              params={{ gameId: item.game.id }}
              className={cn(
                'grid gap-3 px-6 py-4 transition-colors hover:bg-muted/50',
                'md:grid-cols-[minmax(0,2fr)_minmax(0,1.5fr)_auto_auto_auto] md:items-center md:gap-4',
              )}
            >
              <div className="min-w-0">
                <p className="truncate font-medium">{item.game.name}</p>
              </div>
              <p className="truncate text-sm text-muted-foreground md:max-w-none">
                {item.game.description || '—'}
              </p>
              <div className="text-sm">
                <span className="text-muted-foreground md:hidden">Updated </span>
                <span className="font-medium">
                  {formatRelativeTime(item.game.updatedAt)}
                </span>
              </div>
              <div className="text-sm">
                <span className="text-muted-foreground md:hidden">Versions </span>
                <span className="font-medium tabular-nums">{item.versionCount}</span>
              </div>
              <GameStatusBadge label={item.statusLabel} status={item.status} />
            </Link>
          </li>
        ))}
      </ul>
    </Card>
  )
}
