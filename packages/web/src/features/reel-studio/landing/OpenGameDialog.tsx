import { Link } from '@tanstack/react-router'
import { useState } from 'react'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { useGames } from '@/features/games/hooks/use-games'
import { useGameVersions } from '@/features/games/hooks/use-games'

function GameVersionRow({ gameId, gameName }: { gameId: string; gameName: string }) {
  const versions = useGameVersions(gameId)

  if (versions.isLoading) {
    return <Skeleton className="h-10 w-full" />
  }

  const latest = versions.data?.[versions.data.length - 1]
  if (!latest) {
    return (
      <div className="flex items-center justify-between rounded-md border px-3 py-2">
        <span className="text-sm">{gameName}</span>
        <Button size="sm" variant="outline" asChild>
          <Link to="/games/$gameId" params={{ gameId }}>
            Open game
          </Link>
        </Button>
      </div>
    )
  }

  return (
    <Link
      to="/games/$gameId/versions/$versionId/reel-studio"
      params={{ gameId, versionId: latest.id }}
      className="flex items-center justify-between rounded-md border px-3 py-2 transition-colors hover:bg-muted/50"
    >
      <div>
        <p className="text-sm font-medium">{gameName}</p>
        <p className="text-xs text-muted-foreground">v{latest.version}</p>
      </div>
      <span className="text-xs text-primary">Open studio</span>
    </Link>
  )
}

export function OpenGameDialog({
  open,
  onOpenChange,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const [search, setSearch] = useState('')
  const games = useGames({ page: 1, pageSize: 50 })

  const items =
    games.data?.items.filter((game) =>
      game.name.toLowerCase().includes(search.toLowerCase()),
    ) ?? []

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Open existing game</DialogTitle>
        </DialogHeader>
        <Input
          placeholder="Search games…"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          className="mb-3"
        />
        <div className="max-h-80 space-y-2 overflow-y-auto">
          {games.isLoading &&
            Array.from({ length: 4 }).map((_, index) => (
              <Skeleton key={index} className="h-10 w-full" />
            ))}
          {items.map((game) => (
            <GameVersionRow key={game.id} gameId={game.id} gameName={game.name} />
          ))}
          {!games.isLoading && items.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">No games found.</p>
          ) : null}
        </div>
      </DialogContent>
    </Dialog>
  )
}
