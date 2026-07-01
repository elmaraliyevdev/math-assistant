import { useQueries } from '@tanstack/react-query'
import { useMemo } from 'react'

import { useDashboardSummary } from '@/features/dashboard/hooks/use-dashboard'
import { gamesApi } from '@/features/games/api/games-api'
import {
  deriveGameStatus,
  gameStatusLabel,
  type GameListStatusFilter,
} from '@/features/games/lib/game-status'
import { gameKeys } from '@/features/games/hooks/use-games'
import type { Game } from '@/types/api'
import type { ProjectStatus } from '@/features/workspace/lib/workspace-status'

export type GameListSort = 'updated' | 'name'

export interface GameListItem {
  game: Game
  versions: import('@/types/api').GameVersionSummary[]
  versionCount: number
  status: ProjectStatus
  statusLabel: string
}

export function useGamesWithStatus(games: Game[] | undefined) {
  const summary = useDashboardSummary()
  const recentSimulations = summary.data?.recentSimulations ?? []

  const versionQueries = useQueries({
    queries: (games ?? []).map((game) => ({
      queryKey: gameKeys.versions(game.id),
      queryFn: () => gamesApi.listVersions(game.id),
      staleTime: 60_000,
    })),
  })

  const items = useMemo((): GameListItem[] => {
    if (!games) return []
    return games.map((game, index) => {
      const versions = versionQueries[index]?.data ?? []
      const status = deriveGameStatus(versions, recentSimulations)
      return {
        game,
        versions,
        versionCount: versions.length,
        status,
        statusLabel: gameStatusLabel(status, versions, recentSimulations),
      }
    })
  }, [games, versionQueries, recentSimulations])

  const versionsLoading = versionQueries.some((query) => query.isLoading)

  return { items, versionsLoading, recentSimulations }
}

export function filterAndSortGames(
  items: GameListItem[],
  filter: GameListStatusFilter,
  sort: GameListSort,
): GameListItem[] {
  let next = items
  if (filter !== 'all') {
    next = next.filter((item) => item.status === filter)
  }
  return [...next].sort((a, b) => {
    if (sort === 'name') {
      return a.game.name.localeCompare(b.game.name)
    }
    return new Date(b.game.updatedAt).getTime() - new Date(a.game.updatedAt).getTime()
  })
}
