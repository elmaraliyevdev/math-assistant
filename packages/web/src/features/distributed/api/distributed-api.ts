import { api } from '@/services/api'

export interface SimulationShard {
  id: string
  simulationId: string
  shardIndex: number
  spinCount: number
  status: string
  workerId: string | null
  startedAt: string | null
  completedAt: string | null
  errorMessage: string | null
}

export interface SimulationShardList {
  items: SimulationShard[]
  totalShards: number
  completedShards: number
  failedShards: number
  progressPercentage: number
}

export interface SimulationQueueSummary {
  pendingTasks: number
  runningTasks: number
  completedTasks: number
  failedTasks: number
  averageSimulationDurationSeconds: number | null
}

export interface WorkerList {
  activeWorkers: number
  items: Array<{
    workerId: string
    status: string
    activeTasks: number
    processedTasks: number
  }>
}

export const distributedApi = {
  async listShards(simulationId: string) {
    const { data } = await api.get<SimulationShardList>(
      `/simulations/${simulationId}/shards`,
    )
    return data
  },

  async retryFailed(simulationId: string) {
    const { data } = await api.post<{ simulationId: string; retriedShards: number }>(
      `/simulations/${simulationId}/retry`,
    )
    return data
  },

  async getQueue() {
    const { data } = await api.get<SimulationQueueSummary>('/simulations/queue')
    return data
  },

  async listWorkers() {
    const { data } = await api.get<WorkerList>('/workers')
    return data
  },
}
