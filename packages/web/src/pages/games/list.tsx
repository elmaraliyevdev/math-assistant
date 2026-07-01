import { useMemo, useState } from 'react'

import { PageLayout } from '@/components/design-system'
import { Button } from '@/components/ui/button'
import { GameProjectList } from '@/features/games/components/GameProjectList'
import { GamesEmptyState, GamesToolbar } from '@/features/games/components/GamesToolbar'
import { useGames } from '@/features/games/hooks/use-games'
import {
  filterAndSortGames,
  useGamesWithStatus,
} from '@/features/games/hooks/use-games-with-status'
import type { GameListStatusFilter } from '@/features/games/lib/game-status'
import type { GameListSort } from '@/features/games/hooks/use-games-with-status'
import { useDebouncedValue } from '@/hooks/use-debounced-value'

const PAGE_SIZE = 20

export function GamesListPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState<GameListStatusFilter>('all')
  const [sort, setSort] = useState<GameListSort>('updated')
  const debouncedSearch = useDebouncedValue(search)

  const games = useGames({
    page,
    pageSize: PAGE_SIZE,
    search: debouncedSearch || undefined,
  })
  const { items, versionsLoading } = useGamesWithStatus(games.data?.items)
  const visibleItems = useMemo(
    () => filterAndSortGames(items, filter, sort),
    [items, filter, sort],
  )

  const totalPages = games.data ? Math.ceil(games.data.total / PAGE_SIZE) : 0
  const loading = games.isLoading || versionsLoading
  const showEmpty = !loading && visibleItems.length === 0

  return (
    <PageLayout>
      <GamesToolbar
        search={search}
        onSearchChange={(value) => {
          setSearch(value)
          setPage(1)
        }}
        filter={filter}
        onFilterChange={setFilter}
        sort={sort}
        onSortChange={setSort}
      />

      {!showEmpty && <GameProjectList items={visibleItems} loading={loading} />}

      {showEmpty && <GamesEmptyState hasSearch={Boolean(debouncedSearch) || filter !== 'all'} />}

      {games.data && games.data.total > PAGE_SIZE && (
        <div className="mt-8 flex items-center justify-between text-sm text-muted-foreground">
          <p>Page {page} of {totalPages}</p>
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
    </PageLayout>
  )
}
