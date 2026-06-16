import { Link } from '@tanstack/react-router'
import { Plus } from 'lucide-react'
import { useState } from 'react'

import { ConfirmDialog } from '@/components/ui/confirm-dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useMe } from '@/features/auth/use-auth'
import {
  GameEditDialog,
  GameTable,
  GameTableEmpty,
} from '@/features/games/components'
import { useDeleteGame, useGames } from '@/features/games/hooks/use-games'
import { useGameTableRows } from '@/features/games/hooks/use-game-table-rows'
import type { GameTableRow } from '@/features/games/types'
import { useDebouncedValue } from '@/hooks/use-debounced-value'

const PAGE_SIZE = 10

export function GamesListPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const debouncedSearch = useDebouncedValue(search)
  const { data: me } = useMe()
  const games = useGames({
    page,
    pageSize: PAGE_SIZE,
    search: debouncedSearch || undefined,
  })
  const rows = useGameTableRows(games.data?.items, me?.organizations)
  const deleteGame = useDeleteGame()
  const [editGame, setEditGame] = useState<GameTableRow | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<GameTableRow | null>(null)

  const totalPages = games.data ? Math.ceil(games.data.total / PAGE_SIZE) : 0

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Games</h2>
          <p className="text-muted-foreground">Manage slot games in your organization.</p>
        </div>
        <Button asChild>
          <Link to="/games/create">
            <Plus className="h-4 w-4" />
            Create game
          </Link>
        </Button>
      </div>

      <Input
        placeholder="Search by game name…"
        value={search}
        onChange={(event) => {
          setSearch(event.target.value)
          setPage(1)
        }}
        className="max-w-md"
      />

      <GameTable
        rows={rows}
        loading={games.isLoading}
        onEdit={setEditGame}
        onDelete={setDeleteTarget}
      />

      {!games.isLoading && rows.length === 0 && (
        <GameTableEmpty hasSearch={Boolean(debouncedSearch)} />
      )}

      {games.data && games.data.total > PAGE_SIZE && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Page {page} of {totalPages} · {games.data.total} games
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}

      <GameEditDialog
        game={editGame}
        open={Boolean(editGame)}
        onOpenChange={(open) => !open && setEditGame(null)}
      />

      <ConfirmDialog
        open={Boolean(deleteTarget)}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title="Delete game"
        description={`Delete "${deleteTarget?.name}"? This cannot be undone.`}
        confirmLabel="Delete"
        destructive
        loading={deleteGame.isPending}
        onConfirm={() => {
          if (deleteTarget) {
            deleteGame.mutate(deleteTarget.id, {
              onSuccess: () => setDeleteTarget(null),
            })
          }
        }}
      />
    </div>
  )
}
