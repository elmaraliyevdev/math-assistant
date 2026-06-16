import { useQueries } from '@tanstack/react-query'
import { useMemo } from 'react'

import { gamesApi } from '@/features/games/api/games-api'
import { gameKeys } from '@/features/games/hooks/use-games'
import { simulationsApi } from '@/features/simulations/api/simulations-api'
import { simulationKeys } from '@/features/simulations/hooks/use-simulations'
import type { SimulationTableRow } from '@/features/simulations/types'
import type {
  Game,
  GameVersionSummary,
  OrganizationMembership,
  SimulationSummary,
} from '@/types/api'

interface VersionLookup {
  gameId: string
  gameName: string
  organizationId: string
  versionNumber: number
}

function buildVersionLookup(
  games: Game[],
  versionLists: (GameVersionSummary[] | undefined)[],
): Map<string, VersionLookup> {
  const lookup = new Map<string, VersionLookup>()

  games.forEach((game, index) => {
    for (const version of versionLists[index] ?? []) {
      lookup.set(version.id, {
        gameId: game.id,
        gameName: game.name,
        organizationId: game.organizationId,
        versionNumber: version.version,
      })
    }
  })

  return lookup
}

export function useSimulationTableRows(
  simulations: SimulationSummary[] | undefined,
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

  const completedIds = useMemo(
    () =>
      (simulations ?? [])
        .filter((simulation) => simulation.status === 'completed')
        .map((simulation) => simulation.id),
    [simulations],
  )

  const resultQueries = useQueries({
    queries: completedIds.map((simulationId) => ({
      queryKey: simulationKeys.results(simulationId),
      queryFn: () => simulationsApi.getResults(simulationId),
      staleTime: 60_000,
    })),
  })

  const resultsById = useMemo(() => {
    const map = new Map<string, (typeof resultQueries)[number]['data']>()
    completedIds.forEach((simulationId, index) => {
      const data = resultQueries[index]?.data
      if (data) {
        map.set(simulationId, data)
      }
    })
    return map
  }, [completedIds, resultQueries])

  return useMemo(() => {
    if (!simulations) {
      return []
    }

    const orgMap = new Map(
      (organizations ?? []).map((org) => [org.organizationId, org.organizationName]),
    )
    const versionLookup = buildVersionLookup(
      games ?? [],
      versionQueries.map((query) => query.data),
    )

    return simulations.map((simulation): SimulationTableRow => {
      const version = versionLookup.get(simulation.gameVersionId)
      const results = resultsById.get(simulation.id)

      return {
        ...simulation,
        gameName: version?.gameName ?? 'Unknown game',
        gameId: version?.gameId ?? null,
        versionNumber: version?.versionNumber ?? null,
        organizationName:
          orgMap.get(version?.organizationId ?? '') ??
          version?.organizationId ??
          '—',
        rtp: results?.summary.rtp ?? null,
        totalBetMinorUnits: results?.totals.totalBetMinorUnits ?? null,
        totalWinMinorUnits: results?.totals.totalWinMinorUnits ?? null,
      }
    })
  }, [games, organizations, resultQueries, simulations, versionQueries])
}
