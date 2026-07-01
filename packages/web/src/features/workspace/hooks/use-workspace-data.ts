import { useQueries } from '@tanstack/react-query'
import { useMemo } from 'react'

import { useDashboardSummary } from '@/features/dashboard/hooks/use-dashboard'
import { gamesApi } from '@/features/games/api/games-api'
import { gameKeys, useGames } from '@/features/games/hooks/use-games'
import { buildCopilotInsights } from '@/features/workspace/lib/workspace-copilot'
import {
  getContinueStatusLabel,
  getDesignHealthScore,
  getLatestVersion,
  getProjectStatus,
  projectStatusLabelForDesigning,
  simulationsForGame,
} from '@/features/workspace/lib/workspace-status'
import type { DashboardSimulationSummary } from '@/services/dashboard'
import type { Game, GameVersionSummary } from '@/types/api'

export interface WorkspaceProject {
  game: Game
  versions: GameVersionSummary[]
  latestVersion: GameVersionSummary | null
  status: ReturnType<typeof getProjectStatus>
  statusLabel: string
  latestSimulation: DashboardSimulationSummary | null
}

export function useWorkspaceData() {
  const summary = useDashboardSummary()
  const gamesQuery = useGames({ page: 1, pageSize: 20 })

  const sortedGames = useMemo(() => {
    const items = gamesQuery.data?.items ?? []
    return [...items].sort(
      (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime(),
    )
  }, [gamesQuery.data?.items])

  const topGames = sortedGames.slice(0, 8)

  const versionQueries = useQueries({
    queries: topGames.map((game) => ({
      queryKey: gameKeys.versions(game.id),
      queryFn: () => gamesApi.listVersions(game.id),
      staleTime: 60_000,
    })),
  })

  const versionsByGameId = useMemo(() => {
    const map: Record<string, GameVersionSummary[]> = {}
    topGames.forEach((game, index) => {
      map[game.id] = versionQueries[index]?.data ?? []
    })
    return map
  }, [topGames, versionQueries])

  const recentSimulations = summary.data?.recentSimulations ?? []

  const projects = useMemo((): WorkspaceProject[] => {
    return topGames.map((game) => {
      const versions = versionsByGameId[game.id] ?? []
      const latestVersion = getLatestVersion(versions)
      const versionIds = versions.map((version) => version.id)
      const gameSims = simulationsForGame(versionIds, recentSimulations)
      const latestSimulation = gameSims[0] ?? null
      const status = getProjectStatus(versions, recentSimulations)
      const hasSimulation = gameSims.length > 0

      return {
        game,
        versions,
        latestVersion,
        status,
        statusLabel: projectStatusLabelForDesigning(status, hasSimulation),
        latestSimulation,
      }
    })
  }, [topGames, versionsByGameId, recentSimulations])

  const continueTarget = projects[0] ?? null

  const continueMeta = useMemo(() => {
    if (!continueTarget?.latestVersion) {
      return null
    }
    const { game, latestVersion, status, latestSimulation } = continueTarget
    const versionSims = simulationsForGame([latestVersion.id], recentSimulations)
    const lastSim = versionSims[0] ?? latestSimulation

    return {
      gameId: game.id,
      gameName: game.name,
      versionId: latestVersion.id,
      versionNumber: latestVersion.version,
      lastEditedAt: game.updatedAt,
      designHealth: getDesignHealthScore(status, lastSim),
      lastSimulationRtp: lastSim?.rtp ?? null,
      statusLabel: getContinueStatusLabel(status, lastSim),
      projectStatus: status,
    }
  }, [continueTarget, recentSimulations])

  const workspaceHealth = useMemo(() => {
    const data = summary.data
    if (!data) return null

    const failedJobs = data.recentSimulations.filter((item) => item.status === 'failed').length
    const needsAttention =
      data.pendingReviews.length +
      data.outsideRtpTolerance.length +
      data.myPendingReviews.length

    return {
      games: data.totalGames,
      readyForCertification: data.certificationReady.length,
      runningSimulations: data.activeSimulations,
      needsAttention,
      failedJobs,
    }
  }, [summary.data])

  const copilotInsights = useMemo(() => {
    if (!summary.data) return []
    const versionIdsByGame: Record<string, string[]> = {}
    for (const [gameId, versions] of Object.entries(versionsByGameId)) {
      versionIdsByGame[gameId] = versions.map((version) => version.id)
    }
    return buildCopilotInsights({
      games: sortedGames,
      versionIdsByGame,
      recentSimulations,
      certificationReadyCount: summary.data.certificationReady.length,
      outsideRtpCount: summary.data.outsideRtpTolerance.length,
      recommendedActions: summary.data.recommendedActions,
    })
  }, [summary.data, sortedGames, versionsByGameId, recentSimulations])

  const notifications = summary.data?.recentNotifications ?? []

  const isLoading =
    summary.isLoading || gamesQuery.isLoading || versionQueries.some((query) => query.isLoading)

  return {
    isLoading,
    hasGames: (gamesQuery.data?.total ?? 0) > 0,
    continueMeta,
    workspaceHealth,
    copilotInsights,
    projects: projects.slice(0, 5),
    recentSimulations: recentSimulations.slice(0, 5),
    notifications: notifications.slice(0, 5),
  }
}
