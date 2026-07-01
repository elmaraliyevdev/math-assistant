import type { DashboardSummary } from '@web/services/dashboard-types'

import { DEMO_ORGANIZATION_ID, DEMO_SIMULATION_ID, DEMO_VERSION_ID } from './constants'
import { demoGame } from './games'

export const demoDashboardSummary: DashboardSummary = {
  totalGames: 12,
  totalSimulations: 48,
  activeSimulations: 1,
  averageRtp: 0.9584,
  recentNotifications: [
    {
      id: 'notif-sim-complete',
      type: 'simulation_completed',
      title: 'Simulation completed',
      message: `10M-spin run for ${demoGame.name} finished within RTP tolerance.`,
      organizationId: DEMO_ORGANIZATION_ID,
      entityType: 'simulation',
      entityId: DEMO_SIMULATION_ID,
      readAt: null,
      createdAt: '2026-06-15T09:42:00Z',
    },
  ],
  recentActivity: [
    {
      id: 'audit-reel-edit',
      userId: 'user-elena',
      userEmail: 'elena.k@mathstudio.io',
      userName: 'Elena Kowalski',
      organizationId: DEMO_ORGANIZATION_ID,
      action: 'game_version.create',
      entityType: 'game_version',
      entityId: DEMO_VERSION_ID,
      metadata: { gameName: demoGame.name, version: 3 },
      createdAt: '2026-06-10T14:30:00Z',
    },
  ],
  pendingReviews: [],
  myPendingReviews: [],
  certificationReady: [
    {
      simulationId: DEMO_SIMULATION_ID,
      gameVersionId: DEMO_VERSION_ID,
      workflowStatus: 'approved',
      updatedAt: '2026-06-14T08:00:00Z',
    },
  ],
  recentlyApproved: [],
  recentSimulations: [
    {
      simulationId: DEMO_SIMULATION_ID,
      gameVersionId: DEMO_VERSION_ID,
      gameName: demoGame.name,
      gameVersionLabel: 'v3',
      status: 'completed',
      workflowStatus: 'approved',
      spinCount: 10_000_000,
      rtp: 0.9596,
      withinRtpTolerance: true,
      createdAt: '2026-06-14T08:00:00Z',
    },
    {
      simulationId: 'sim-neon-fruits-1204',
      gameVersionId: 'version-neon-v2',
      gameName: 'Neon Fruits',
      gameVersionLabel: 'v2',
      status: 'running',
      workflowStatus: 'draft',
      spinCount: 5_000_000,
      rtp: null,
      withinRtpTolerance: null,
      createdAt: '2026-06-15T07:15:00Z',
    },
  ],
  outsideRtpTolerance: [],
  recommendedActions: [
    {
      id: 'continue-crown-quest',
      label: 'Continue editing Crown Quest',
      description: 'Version 3 was updated yesterday — resume reel strip work.',
      href: '/reel-studio',
    },
    {
      id: 'review-certification',
      label: 'Review certification package',
      description: 'Crown Quest v3 is cleared for certification export.',
      href: '/mathematics',
    },
  ],
}
