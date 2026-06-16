import { useQueries } from '@tanstack/react-query'
import { useMemo } from 'react'

import { gamesApi } from '@/features/games/api/games-api'
import { gameKeys } from '@/features/games/hooks/use-games'
import type { GameTableRow } from '@/features/games/types'
import type { Game, OrganizationMembership } from '@/types/api'

export function useGameTableRows(
  games: Game[] | undefined,
  organizations: OrganizationMembership[] | undefined,
) {
  const versionQueries = useQueries({
    queries: (games ?? []).map((game) => ({
      queryKey: gameKeys.versions(game.id),
      queryFn: () => gamesApi.listVersions(game.id),
      staleTime: 60_000,
    })),
  })

  return useMemo(() => {
    if (!games) {
      return []
    }

    const orgMap = new Map(
      (organizations ?? []).map((org) => [org.organizationId, org.organizationName]),
    )

    return games.map((game, index): GameTableRow => ({
      ...game,
      organizationName: orgMap.get(game.organizationId) ?? game.organizationId,
      versionCount: versionQueries[index]?.data?.length ?? 0,
    }))
  }, [games, organizations, versionQueries])
}
