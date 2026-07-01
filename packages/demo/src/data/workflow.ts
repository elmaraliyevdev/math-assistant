import type {
  SimulationActivity,
  SimulationComment,
  SimulationWorkflow,
} from '@/features/collaboration/types'

import { DEMO_SIMULATION_ID } from './constants'

export const demoSimulationWorkflow: SimulationWorkflow = {
  simulationId: DEMO_SIMULATION_ID,
  status: 'approved',
  reviews: [
    {
      id: 'review-1',
      simulationId: DEMO_SIMULATION_ID,
      reviewerId: 'user-senior-math',
      reviewerName: 'Marcus T.',
      reviewerRole: 'admin',
      status: 'approved',
      decisionReason: 'RTP within tolerance; volatility matches spec.',
      createdAt: '2026-06-14T11:20:00Z',
      updatedAt: '2026-06-14T11:20:00Z',
    },
  ],
  approvals: [
    {
      id: 'approval-1',
      simulationId: DEMO_SIMULATION_ID,
      approvedBy: 'user-math',
      approvalStage: 'mathematician',
      approvedAt: '2026-06-12T14:32:00Z',
    },
    {
      id: 'approval-2',
      simulationId: DEMO_SIMULATION_ID,
      approvedBy: 'user-senior-math',
      approvalStage: 'senior_mathematician',
      approvedAt: '2026-06-14T09:15:00Z',
    },
    {
      id: 'approval-3',
      simulationId: DEMO_SIMULATION_ID,
      approvedBy: 'user-po',
      approvalStage: 'product_owner',
      approvedAt: '2026-06-15T16:40:00Z',
    },
  ],
}

export const demoSimulationComments: SimulationComment[] = [
  {
    id: 'comment-1',
    simulationId: DEMO_SIMULATION_ID,
    userId: 'user-math',
    authorName: 'Elena K.',
    authorRole: 'mathematician',
    content:
      'Scatter frequency on reel 3 adjusted — observed trigger rate now within 0.02 pp of theoretical.',
    createdAt: '2026-06-15T10:12:00Z',
  },
  {
    id: 'comment-2',
    simulationId: DEMO_SIMULATION_ID,
    userId: 'user-senior-math',
    authorName: 'Marcus T.',
    authorRole: 'admin',
    content:
      'RTP gap cleared. Volatility index matches spec. Ready for producer sign-off.',
    createdAt: '2026-06-15T14:28:00Z',
  },
]

export const demoSimulationActivity: SimulationActivity[] = [
  {
    id: 'activity-1',
    simulationId: DEMO_SIMULATION_ID,
    actorId: 'system',
    action: 'simulation_completed',
    metadata: { rtp: '95.96%' },
    createdAt: '2026-06-15T14:32:08Z',
  },
  {
    id: 'activity-2',
    simulationId: DEMO_SIMULATION_ID,
    actorId: 'user-math',
    action: 'calibration_pass',
    metadata: { rtp: '95.96%' },
    createdAt: '2026-06-15T14:28:41Z',
  },
  {
    id: 'activity-3',
    simulationId: DEMO_SIMULATION_ID,
    actorId: 'user-senior-math',
    action: 'review_approved',
    metadata: null,
    createdAt: '2026-06-15T13:15:22Z',
  },
  {
    id: 'activity-4',
    simulationId: DEMO_SIMULATION_ID,
    actorId: 'user-dev',
    action: 'reel_studio_saved',
    metadata: { version: 'v3.2' },
    createdAt: '2026-06-15T11:04:17Z',
  },
]
