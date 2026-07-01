import type { DashboardSimulationSummary } from '@/services/dashboard'
import type { GameVersionSummary } from '@/types/api'

import {
  getDesignHealthScore,
  getProjectStatus,
  PROJECT_STATUS_LABELS,
  PROJECT_STATUS_STYLES,
  projectStatusLabelForDesigning,
  simulationsForGame,
  type ProjectStatus,
} from '@/features/workspace/lib/workspace-status'

export type GameListStatusFilter = 'all' | ProjectStatus

export const GAME_LIST_STATUS_LABELS: Record<ProjectStatus, string> = {
  draft: 'Draft',
  designing: 'Designing',
  ready: 'Ready',
  simulating: 'Simulating',
  review: 'Needs review',
  certified: 'Certified',
  needs_attention: 'Needs attention',
}

export type VersionDisplayStatus =
  | 'designing'
  | 'ready'
  | 'certified'
  | 'simulating'
  | 'review'
  | 'needs_attention'
  | 'archived'

export const VERSION_STATUS_LABELS: Record<VersionDisplayStatus, string> = {
  designing: 'Designing',
  ready: 'Ready',
  certified: 'Certified',
  simulating: 'Simulating',
  review: 'Needs review',
  needs_attention: 'Needs attention',
  archived: 'Archived',
}

export const VERSION_STATUS_STYLES: Record<VersionDisplayStatus, string> = {
  designing: PROJECT_STATUS_STYLES.designing,
  ready: PROJECT_STATUS_STYLES.ready,
  certified: PROJECT_STATUS_STYLES.certified,
  simulating: PROJECT_STATUS_STYLES.simulating,
  review: PROJECT_STATUS_STYLES.review,
  needs_attention: PROJECT_STATUS_STYLES.needs_attention,
  archived: 'bg-muted text-muted-foreground',
}

export function deriveGameStatus(
  versions: GameVersionSummary[],
  simulations: DashboardSimulationSummary[],
): ProjectStatus {
  return getProjectStatus(versions, simulations)
}

export function gameStatusLabel(
  status: ProjectStatus,
  versions: GameVersionSummary[],
  simulations: DashboardSimulationSummary[],
): string {
  const versionIds = versions.map((version) => version.id)
  const hasSimulation = simulationsForGame(versionIds, simulations).length > 0
  if (status === 'review') return GAME_LIST_STATUS_LABELS.review
  if (status === 'needs_attention') return GAME_LIST_STATUS_LABELS.needs_attention
  return projectStatusLabelForDesigning(status, hasSimulation)
}

export function deriveVersionStatus(
  version: GameVersionSummary,
  latestVersion: GameVersionSummary | null,
  simulation: DashboardSimulationSummary | null,
): VersionDisplayStatus {
  if (latestVersion && version.id !== latestVersion.id) {
    return 'archived'
  }
  if (!simulation) return 'designing'
  if (simulation.workflowStatus === 'approved') return 'certified'
  if (simulation.workflowStatus === 'certification_ready') return 'ready'
  if (simulation.workflowStatus === 'under_review') return 'review'
  if (simulation.status === 'running' || simulation.status === 'pending') return 'simulating'
  if (simulation.withinRtpTolerance === false || simulation.status === 'failed') {
    return 'needs_attention'
  }
  if (simulation.status === 'completed') return 'ready'
  return 'designing'
}

export function versionDesignHealth(
  status: VersionDisplayStatus,
  simulation: DashboardSimulationSummary | null,
): number | null {
  if (status === 'archived') return null
  const mapped: ProjectStatus =
    status === 'review'
      ? 'review'
      : status === 'needs_attention'
        ? 'needs_attention'
        : status === 'certified'
          ? 'certified'
          : status === 'ready'
            ? 'ready'
            : status === 'simulating'
              ? 'simulating'
              : 'designing'
  return getDesignHealthScore(mapped, simulation)
}

export { PROJECT_STATUS_LABELS, PROJECT_STATUS_STYLES }
