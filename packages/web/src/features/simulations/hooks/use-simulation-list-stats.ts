import { useMemo } from 'react'

import { formatDurationMs } from '@/features/simulations/utils/workbench'
import { simulationDurationMs } from '@/features/simulations/utils/health-score'
import type { SimulationTableRow } from '@/features/simulations/types'
import { useSimulations } from '@/features/simulations/hooks/use-simulations'
import { formatPercent } from '@/lib/utils'

export function useSimulationListStats(rows: SimulationTableRow[]) {
  const completedQuery = useSimulations({ page: 1, pageSize: 1, status: 'completed' })
  const runningQuery = useSimulations({ page: 1, pageSize: 1, status: 'running' })
  const failedQuery = useSimulations({ page: 1, pageSize: 1, status: 'failed' })
  const pendingQuery = useSimulations({ page: 1, pageSize: 1, status: 'pending' })

  const derived = useMemo(() => {
    const completedRows = rows.filter((row) => row.status === 'completed')
    const rtpValues = completedRows
      .map((row) => row.rtp)
      .filter((value): value is number => value != null)
    const avgRtp =
      rtpValues.length > 0
        ? rtpValues.reduce((sum, value) => sum + value, 0) / rtpValues.length
        : null

    const durations = completedRows
      .map((row) => simulationDurationMs(row.createdAt, row.completedAt))
      .filter((value): value is number => value != null)
    const avgDurationMs =
      durations.length > 0
        ? durations.reduce((sum, value) => sum + value, 0) / durations.length
        : null

    return {
      avgRtp: avgRtp != null ? formatPercent(avgRtp) : '—',
      avgDuration: formatDurationMs(avgDurationMs),
    }
  }, [rows])

  return {
    completed: completedQuery.data?.total ?? 0,
    running: runningQuery.data?.total ?? 0,
    failed: failedQuery.data?.total ?? 0,
    queued: pendingQuery.data?.total ?? 0,
    avgRtp: derived.avgRtp,
    avgDuration: derived.avgDuration,
    isLoading:
      completedQuery.isLoading ||
      runningQuery.isLoading ||
      failedQuery.isLoading ||
      pendingQuery.isLoading,
  }
}
