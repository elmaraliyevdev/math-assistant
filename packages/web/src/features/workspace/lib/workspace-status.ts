import type { DashboardSimulationSummary } from '@/services/dashboard'
import type { GameVersionSummary } from '@/types/api'

export type ProjectStatus =
  | 'designing'
  | 'ready'
  | 'simulating'
  | 'review'
  | 'certified'
  | 'needs_attention'
  | 'draft'

export const PROJECT_STATUS_LABELS: Record<ProjectStatus, string> = {
  designing: 'Designing',
  ready: 'Ready',
  simulating: 'Simulating',
  review: 'Review',
  certified: 'Certified',
  needs_attention: 'Needs attention',
  draft: 'Draft',
}

export const PROJECT_STATUS_STYLES: Record<ProjectStatus, string> = {
  designing: 'bg-slate-500/10 text-slate-700 dark:text-slate-300',
  ready: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400',
  simulating: 'bg-blue-500/10 text-blue-700 dark:text-blue-400',
  review: 'bg-amber-500/10 text-amber-800 dark:text-amber-300',
  certified: 'bg-primary/10 text-primary',
  needs_attention: 'bg-red-500/10 text-red-700 dark:text-red-400',
  draft: 'bg-muted text-muted-foreground',
}

export function getLatestVersion(versions: GameVersionSummary[] | undefined) {
  if (!versions?.length) return null
  return [...versions].sort((a, b) => b.version - a.version)[0]
}

export function simulationsForGame(
  versionIds: string[],
  simulations: DashboardSimulationSummary[],
) {
  const idSet = new Set(versionIds)
  return simulations.filter((item) => idSet.has(item.gameVersionId))
}

export function getProjectStatus(
  versions: GameVersionSummary[] | undefined,
  simulations: DashboardSimulationSummary[],
): ProjectStatus {
  if (!versions?.length) return 'draft'

  const versionIds = versions.map((version) => version.id)
  const gameSims = simulationsForGame(versionIds, simulations)

  if (gameSims.some((item) => item.status === 'running' || item.status === 'pending')) {
    return 'simulating'
  }
  if (gameSims.some((item) => item.workflowStatus === 'approved')) {
    return 'certified'
  }
  if (gameSims.some((item) => item.workflowStatus === 'certification_ready')) {
    return 'ready'
  }
  if (gameSims.some((item) => item.workflowStatus === 'under_review')) {
    return 'review'
  }
  if (
    gameSims.some(
      (item) => item.status === 'failed' || item.withinRtpTolerance === false,
    )
  ) {
    return 'needs_attention'
  }
  if (!gameSims.length) {
    return 'designing'
  }
  return 'designing'
}

export function getDesignHealthScore(
  status: ProjectStatus,
  latestSimulation: DashboardSimulationSummary | null,
): number | null {
  switch (status) {
    case 'certified':
    case 'ready':
      return 98
    case 'review':
      return 92
    case 'simulating':
      return 90
    case 'needs_attention':
      return latestSimulation?.withinRtpTolerance === false ? 72 : 68
    case 'draft':
      return null
    case 'designing':
      return latestSimulation ? 85 : null
    default:
      return 88
  }
}

export function getContinueStatusLabel(
  status: ProjectStatus,
  latestSimulation: DashboardSimulationSummary | null,
): string {
  if (status === 'ready' || status === 'certified') {
    return 'Ready for certification'
  }
  if (status === 'simulating') {
    return 'Simulation in progress'
  }
  if (status === 'review') {
    return 'Awaiting review'
  }
  if (status === 'needs_attention') {
    return 'Needs attention'
  }
  if (!latestSimulation) {
    return 'Ready for simulation'
  }
  if (latestSimulation.status === 'completed') {
    return 'Ready for simulation'
  }
  return 'Designing'
}

export function projectStatusLabelForDesigning(
  status: ProjectStatus,
  hasSimulation: boolean,
): string {
  if (status === 'designing' && !hasSimulation) {
    return 'Needs simulation'
  }
  return PROJECT_STATUS_LABELS[status]
}
