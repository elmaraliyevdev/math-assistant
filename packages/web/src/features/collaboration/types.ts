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
