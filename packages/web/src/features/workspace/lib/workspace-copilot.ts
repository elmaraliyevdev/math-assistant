import type { DashboardRecommendedAction, DashboardSimulationSummary } from '@/services/dashboard'
import type { Game } from '@/types/api'

import { simulationsForGame } from '@/features/workspace/lib/workspace-status'

export interface CopilotInsight {
  id: string
  text: string
}

export function buildCopilotInsights(input: {
  games: Game[]
  versionIdsByGame: Record<string, string[]>
  recentSimulations: DashboardSimulationSummary[]
  certificationReadyCount: number
  outsideRtpCount: number
  recommendedActions: DashboardRecommendedAction[]
}): CopilotInsight[] {
  const insights: CopilotInsight[] = []
  const seen = new Set<string>()

  const add = (id: string, text: string) => {
    if (seen.has(id)) return
    seen.add(id)
    insights.push({ id, text })
  }

  if (input.certificationReadyCount > 0) {
    const readySim = input.recentSimulations.find(
      (item) => item.workflowStatus === 'certification_ready' && item.gameName,
    )
    const name = readySim?.gameName ?? 'A game'
    add('cert-ready', `${name} is ready for certification.`)
  }

  const neverSimulated = input.games.filter((game) => {
    const versionIds = input.versionIdsByGame[game.id] ?? []
    if (!versionIds.length) return false
    return simulationsForGame(versionIds, input.recentSimulations).length === 0
  })

  for (const game of neverSimulated.slice(0, 2)) {
    add(`never-sim-${game.id}`, `${game.name} has never been simulated.`)
  }

  if (input.outsideRtpCount > 0) {
    const drift = input.recentSimulations.find((item) => item.withinRtpTolerance === false)
    const label = drift?.gameName ?? 'A game'
    add('rtp-drift', `RTP drift detected in ${label}.`)
  }

  const designingWithoutSim = input.games.filter((game) => {
    const versionIds = input.versionIdsByGame[game.id] ?? []
    if (!versionIds.length) return false
    return simulationsForGame(versionIds, input.recentSimulations).length === 0
  })

  if (designingWithoutSim.length >= 2) {
    add(
      'volatility',
      `${designingWithoutSim.length} games can improve volatility.`,
    )
  }

  for (const action of input.recommendedActions) {
    add(`action-${action.id}`, action.description)
  }

  if (!insights.length) {
    add(
      'all-clear',
      'Your workspace looks healthy. Continue designing or run a simulation to validate RTP.',
    )
  }

  return insights.slice(0, 5)
}
