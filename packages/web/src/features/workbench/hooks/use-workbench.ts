import { useQuery } from '@tanstack/react-query'

import { mathematicsApi } from '@/features/mathematics/api/mathematics-api'
import { simulationsApi } from '@/features/simulations/api/simulations-api'

export const workbenchKeys = {
  calibration: (gameVersionId: string, simulationId: string) =>
    ['workbench', 'calibration', gameVersionId, simulationId] as const,
  throughput: ['workbench', 'throughput'] as const,
}

export function useSimulationCalibration(
  gameVersionId: string | undefined,
  simulationId: string | undefined,
  enabled = true,
) {
  return useQuery({
    queryKey: workbenchKeys.calibration(gameVersionId ?? '', simulationId ?? ''),
    queryFn: () =>
      mathematicsApi.calibrate({
        gameVersionId: gameVersionId!,
        simulationId,
      }),
    enabled: enabled && Boolean(gameVersionId) && Boolean(simulationId),
    staleTime: 60_000,
  })
}

export function useSimulationThroughput() {
  return useQuery({
    queryKey: workbenchKeys.throughput,
    queryFn: () => simulationsApi.getThroughput(),
    staleTime: 30_000,
  })
}
