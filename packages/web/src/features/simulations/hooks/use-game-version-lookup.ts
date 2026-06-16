import { useQueries } from '@tanstack/react-query'
import { useMemo } from 'react'

import { gamesApi } from '@/features/games/api/games-api'
import { gameKeys, useGameVersion, useGames } from '@/features/games/hooks/use-games'

export function useGameVersionBySimulation(gameVersionId: string | undefined) {
  const games = useGames({ page: 1, pageSize: 100 })
  const versionQueries = useQueries({
    queries: (games.data?.items ?? []).map((game) => ({
      queryKey: gameKeys.versions(game.id),
      queryFn: () => gamesApi.listVersions(game.id),
      enabled: Boolean(gameVersionId),
      staleTime: 60_000,
    })),
  })

  const lookup = useMemo(() => {
    if (!gameVersionId) return null
    for (const [index, game] of (games.data?.items ?? []).entries()) {
      const versions = versionQueries[index]?.data ?? []
      if (versions.some((version) => version.id === gameVersionId)) {
        return { gameId: game.id, versionId: gameVersionId }
      }
    }
    return null
  }, [gameVersionId, games.data?.items, versionQueries])

  return useGameVersion(lookup?.gameId ?? '', lookup?.versionId ?? '')
}
