import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { distributedApi } from '@/features/distributed/api/distributed-api'
import { simulationKeys } from '@/features/simulations/hooks/use-simulations'

export const distributedKeys = {
  shards: (simulationId: string) => ['distributed', 'shards', simulationId] as const,
  queue: ['distributed', 'queue'] as const,
  workers: ['distributed', 'workers'] as const,
}

export function useSimulationShards(simulationId: string, enabled = true) {
  return useQuery({
    queryKey: distributedKeys.shards(simulationId),
    queryFn: () => distributedApi.listShards(simulationId),
    enabled: enabled && Boolean(simulationId),
    refetchInterval: 2000,
  })
}

export function useRetryFailedShards(simulationId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => distributedApi.retryFailed(simulationId),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: distributedKeys.shards(simulationId),
      })
      void queryClient.invalidateQueries({
        queryKey: simulationKeys.detail(simulationId),
      })
    },
  })
}

export function useSimulationQueue() {
  return useQuery({
    queryKey: distributedKeys.queue,
    queryFn: distributedApi.getQueue,
    refetchInterval: 15_000,
  })
}

export function useWorkers(enabled = true) {
  return useQuery({
    queryKey: distributedKeys.workers,
    queryFn: distributedApi.listWorkers,
    enabled,
    refetchInterval: 15_000,
    retry: false,
  })
}
