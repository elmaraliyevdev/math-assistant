import { api } from '@/services/api'

import type {
  SimulationActivity,
  SimulationApproval,
  SimulationComment,
  SimulationReview,
  SimulationWorkflow,
} from '../types'

export type {
  CollaborationSimulationSummary,
  SimulationActivity,
  SimulationApproval,
  SimulationComment,
  SimulationReview,
  SimulationWorkflow,
} from '../types'

export const collaborationApi = {
  async listComments(simulationId: string) {
    const { data } = await api.get<{ items: SimulationComment[] }>(
      `/simulations/${simulationId}/comments`,
    )
    return data
  },

  async addComment(simulationId: string, content: string) {
    const { data } = await api.post<SimulationComment>(
      `/simulations/${simulationId}/comments`,
      { content },
    )
    return data
  },

  async submitReview(
    simulationId: string,
    payload: { status: string; decisionReason?: string },
  ) {
    const { data } = await api.post<SimulationReview>(
      `/simulations/${simulationId}/review`,
      {
        status: payload.status,
        decisionReason: payload.decisionReason,
      },
    )
    return data
  },

  async approve(simulationId: string, approvalStage: string) {
    const { data } = await api.post<SimulationApproval>(
      `/simulations/${simulationId}/approve`,
      { approvalStage },
    )
    return data
  },

  async getWorkflow(simulationId: string) {
    const { data } = await api.get<SimulationWorkflow>(
      `/simulations/${simulationId}/workflow`,
    )
    return data
  },

  async listActivity(simulationId: string) {
    const { data } = await api.get<{ items: SimulationActivity[] }>(
      `/simulations/${simulationId}/activity`,
    )
    return data
  },

  async transitionWorkflow(simulationId: string, targetStatus: string) {
    const { data } = await api.post<SimulationWorkflow>(
      `/simulations/${simulationId}/workflow/transition`,
      { targetStatus },
    )
    return data
  },
}
