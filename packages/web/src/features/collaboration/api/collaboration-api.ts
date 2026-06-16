import { api } from '@/services/api'

export interface SimulationComment {
  id: string
  simulationId: string
  userId: string
  authorName?: string | null
  authorEmail?: string | null
  authorRole?: string | null
  content: string
  createdAt: string
}

export interface SimulationReview {
  id: string
  simulationId: string
  reviewerId: string
  reviewerName?: string | null
  reviewerEmail?: string | null
  reviewerRole?: string | null
  status: string
  decisionReason: string | null
  createdAt: string
  updatedAt: string
}

export interface SimulationApproval {
  id: string
  simulationId: string
  approvedBy: string
  approvalStage:
    | 'mathematician'
    | 'senior_mathematician'
    | 'product_owner'
    | 'producer'
  approvedAt: string
}

export interface SimulationActivity {
  id: string
  simulationId: string
  actorId: string
  action: string
  metadata: Record<string, unknown> | null
  createdAt: string
}

export interface SimulationWorkflow {
  simulationId: string
  status: string
  reviews: SimulationReview[]
  approvals: SimulationApproval[]
}

export interface CollaborationSimulationSummary {
  simulationId: string
  workflowStatus: string
  gameVersionId: string
  updatedAt: string | null
}

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
