import { api } from '@/services/api'
import type { AuditLog } from '@/services/audit'
import type { Notification } from '@/services/notifications'
import type { CollaborationSimulationSummary } from '@/features/collaboration/api/collaboration-api'

export interface DashboardSummary {
  totalGames: number
  totalSimulations: number
  activeSimulations: number
  averageRtp: number | null
  recentNotifications: Notification[]
  recentActivity: AuditLog[]
  pendingReviews: CollaborationSimulationSummary[]
  myPendingReviews: CollaborationSimulationSummary[]
  certificationReady: CollaborationSimulationSummary[]
  recentlyApproved: CollaborationSimulationSummary[]
  recentSimulations: DashboardSimulationSummary[]
  outsideRtpTolerance: DashboardSimulationSummary[]
  recommendedActions: DashboardRecommendedAction[]
}

export interface DashboardSimulationSummary {
  simulationId: string
  gameVersionId: string
  gameName?: string | null
  gameVersionLabel?: string | null
  status: string
  workflowStatus: string
  spinCount: number
  rtp?: number | null
  withinRtpTolerance?: boolean | null
  createdAt: string
}

export interface DashboardRecommendedAction {
  id: string
  label: string
  description: string
  href: string
}

export const dashboardApi = {
  getSummary() {
    return api
      .get<DashboardSummary>('/dashboard/summary')
      .then((r) => r.data)
  },
}
