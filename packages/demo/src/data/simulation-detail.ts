import type { SimulationDetail } from '@web/types/api'

import { DEMO_SIMULATION_ID, DEMO_VERSION_ID } from './constants'

export const demoSimulationDetailCompleted: SimulationDetail = {
  id: DEMO_SIMULATION_ID,
  gameVersionId: DEMO_VERSION_ID,
  status: 'completed',
  spinCount: 10_000_000,
  completedSpinCount: 10_000_000,
  betMinorUnits: 100,
  eventLogMode: 'summary',
  createdAt: '2026-06-15T08:00:00Z',
  startedAt: '2026-06-15T08:01:12Z',
  completedAt: '2026-06-15T14:32:08Z',
  cancelRequested: false,
  workerId: null,
  errorMessage: null,
  progress: {
    completedSpins: 10_000_000,
    percentage: 100,
  },
  totalShards: 4,
  completedShards: 4,
  failedShards: 0,
  progressPercentage: 100,
  distributedExecution: true,
}

export function buildSimulationDetailProgress(
  completedSpins: number,
  spinCount = 10_000_000,
): SimulationDetail {
  const percentage = Math.min(100, (completedSpins / spinCount) * 100)
  const running = percentage < 100

  return {
    ...demoSimulationDetailCompleted,
    status: running ? 'running' : 'completed',
    completedSpinCount: completedSpins,
    completedAt: running ? null : demoSimulationDetailCompleted.completedAt,
    progress: {
      completedSpins,
      percentage,
    },
    progressPercentage: percentage,
    completedShards: running ? Math.min(3, Math.floor(percentage / 25)) : 4,
  }
}
