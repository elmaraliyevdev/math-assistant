import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { afterAll, afterEach, beforeAll } from 'vitest'

import { certifiedSimulationResults } from './fixtures/certified-results'

const user = {
  id: 'user-1',
  email: 'user@example.com',
  fullName: 'Test User',
  isActive: true,
  createdAt: '2026-01-01T00:00:00Z',
  updatedAt: '2026-01-01T00:00:00Z',
}

export const handlers = [
  http.post('/api/auth/login', async () =>
    HttpResponse.json({
      accessToken: 'access-token',
      refreshToken: 'refresh-token',
      tokenType: 'bearer',
      expiresIn: 900,
    }),
  ),
  http.post('/api/auth/register', async () =>
    HttpResponse.json({
      user,
      organizationId: 'org-1',
      tokens: {
        accessToken: 'access-token',
        refreshToken: 'refresh-token',
        tokenType: 'bearer',
        expiresIn: 900,
      },
    }),
  ),
  http.post('/api/auth/refresh', async () =>
    HttpResponse.json({
      accessToken: 'access-token',
      refreshToken: 'refresh-token',
      tokenType: 'bearer',
      expiresIn: 900,
    }),
  ),
  http.post('/api/auth/logout', async () => new HttpResponse(null, { status: 204 })),
  http.get('/api/auth/me', async () =>
    HttpResponse.json({
      user,
      organizations: [
        {
          organizationId: 'org-1',
          organizationName: 'Workspace',
          organizationSlug: 'workspace',
          role: 'owner',
        },
      ],
    }),
  ),
  http.get('/api/games', async ({ request }) => {
    const url = new URL(request.url)
    const page = Number(url.searchParams.get('page') ?? 1)
    const pageSize = Number(url.searchParams.get('pageSize') ?? 10)
    return HttpResponse.json({
      items: [
        {
          id: 'game-1',
          organizationId: 'org-1',
          name: 'Lucky Stars',
          description: 'Demo slot',
          createdAt: '2026-01-01T00:00:00Z',
          updatedAt: '2026-01-02T00:00:00Z',
        },
      ],
      total: 25,
      page,
      pageSize,
    })
  }),
  http.post('/api/games', async () =>
    HttpResponse.json({
      id: 'game-2',
      organizationId: 'org-1',
      name: 'New Game',
      description: null,
      createdAt: '2026-01-03T00:00:00Z',
      updatedAt: '2026-01-03T00:00:00Z',
    }),
  ),
  http.get('/api/games/:gameId', async () =>
    HttpResponse.json({
      id: 'game-1',
      organizationId: 'org-1',
      name: 'Lucky Stars',
      description: 'Demo slot',
      createdAt: '2026-01-01T00:00:00Z',
      updatedAt: '2026-01-02T00:00:00Z',
    }),
  ),
  http.get('/api/games/:gameId/versions', async () =>
    HttpResponse.json([
      {
        id: 'version-1',
        version: 1,
        contentHash: 'abc123',
        engineVersion: 'runtime-core@1.8.0',
        createdAt: '2026-01-01T00:00:00Z',
      },
    ]),
  ),
  http.get('/api/games/:gameId/versions/:versionId', async () =>
    HttpResponse.json({
      id: 'version-1',
      version: 1,
      contentHash: 'abc123',
      engineVersion: 'runtime-core@1.8.0',
      createdAt: '2026-01-01T00:00:00Z',
      canonicalJson: { schemaVersion: '1.0.0' },
      validationSummary: { passed: true, findingCount: 0, findings: [] },
    }),
  ),
  http.get('/api/simulations', async ({ request }) => {
    const url = new URL(request.url)
    const page = Number(url.searchParams.get('page') ?? 1)
    const pageSize = Number(url.searchParams.get('pageSize') ?? 20)
    return HttpResponse.json({
      items: [
        {
          id: 'sim-1',
          gameVersionId: 'version-1',
          status: 'completed',
          spinCount: 1000,
          completedSpinCount: 1000,
          createdAt: '2026-01-01T00:00:00Z',
          completedAt: '2026-01-01T00:10:00Z',
          errorMessage: null,
        },
        {
          id: 'sim-pending',
          gameVersionId: 'version-1',
          status: 'pending',
          spinCount: 500,
          completedSpinCount: 0,
          createdAt: '2026-01-02T00:00:00Z',
          completedAt: null,
          errorMessage: null,
        },
      ],
      total: 12,
      page,
      pageSize,
    })
  }),
  http.get('/api/simulations/:simulationId', async ({ params }) => {
    const simulationId = String(params.simulationId)
    if (simulationId === 'sim-completed') {
      return HttpResponse.json({
        id: 'sim-completed',
        gameVersionId: 'version-1',
        status: 'completed',
        spinCount: 1000,
        completedSpinCount: 1000,
        betMinorUnits: 100,
        eventLogMode: 'none',
        createdAt: '2026-01-01T00:00:00Z',
        startedAt: '2026-01-01T00:01:00Z',
        completedAt: '2026-01-01T00:10:00Z',
        cancelRequested: false,
        workerId: 'worker-1',
        errorMessage: null,
        progress: { completedSpins: 1000, percentage: 100 },
      })
    }

    return HttpResponse.json({
      id: simulationId,
      gameVersionId: 'version-1',
      status: 'running',
      spinCount: 1000,
      completedSpinCount: 250,
      betMinorUnits: 100,
      eventLogMode: 'none',
      createdAt: '2026-01-01T00:00:00Z',
      startedAt: '2026-01-01T00:01:00Z',
      completedAt: null,
      cancelRequested: false,
      workerId: 'worker-1',
      errorMessage: null,
      progress: { completedSpins: 250, percentage: 25 },
    })
  }),
  http.get('/api/simulations/:simulationId/results', async ({ params }) =>
    HttpResponse.json({
      ...certifiedSimulationResults,
      simulationId: String(params.simulationId),
    }),
  ),
  http.get('/api/organizations', async () =>
    HttpResponse.json({
      items: [
        {
          id: 'org-1',
          name: 'Workspace',
          slug: 'workspace',
          createdAt: '2026-01-01T00:00:00Z',
          updatedAt: '2026-01-01T00:00:00Z',
        },
      ],
    }),
  ),
  http.post('/api/simulations', async () =>
    HttpResponse.json(
      { simulationId: 'sim-2', status: 'pending' },
      { status: 202 },
    ),
  ),
  http.post('/api/simulations/:simulationId/cancel', async () =>
    HttpResponse.json({
      simulationId: 'sim-1',
      status: 'running',
      cancelRequested: true,
    }),
  ),
  http.post('/api/games/:gameId/versions', async () =>
    HttpResponse.json({
      id: 'version-2',
      version: 2,
      contentHash: 'def456',
      engineVersion: 'runtime-core@1.8.0',
      validationSummary: { passed: true, findingCount: 0, findings: [] },
    }),
  ),
  http.patch('/api/games/:gameId', async () =>
    HttpResponse.json({
      id: 'game-1',
      organizationId: 'org-1',
      name: 'Updated Game',
      description: 'Updated',
      createdAt: '2026-01-01T00:00:00Z',
      updatedAt: '2026-01-03T00:00:00Z',
    }),
  ),
  http.delete('/api/games/:gameId', async () => new HttpResponse(null, { status: 204 })),
  http.post('/api/organizations', async () =>
    HttpResponse.json({
      id: 'org-2',
      name: 'Studio',
      slug: 'studio',
      createdAt: '2026-01-01T00:00:00Z',
      updatedAt: '2026-01-01T00:00:00Z',
    }),
  ),
  http.patch('/api/organizations/:organizationId', async () =>
    HttpResponse.json({
      id: 'org-1',
      name: 'Updated Workspace',
      slug: 'updated-workspace',
      createdAt: '2026-01-01T00:00:00Z',
      updatedAt: '2026-01-02T00:00:00Z',
    }),
  ),
  http.post('/api/organizations/:organizationId/members', async () =>
    HttpResponse.json({
      userId: 'user-2',
      organizationId: 'org-1',
      role: 'developer',
      email: 'dev@example.com',
      fullName: 'Developer',
    }),
  ),
  http.delete('/api/organizations/:organizationId/members/:userId', async () =>
    new HttpResponse(null, { status: 204 }),
  ),
  http.get('/api/organizations/:organizationId/members', async () =>
    HttpResponse.json({
      items: [
        {
          userId: 'user-1',
          organizationId: 'org-1',
          role: 'owner',
          email: 'user@example.com',
          fullName: 'Test User',
        },
        {
          userId: 'user-2',
          organizationId: 'org-1',
          role: 'developer',
          email: 'dev@example.com',
          fullName: 'Developer',
        },
      ],
    }),
  ),
  http.get('/api/organizations/:organizationId/invitations', async () =>
    HttpResponse.json({
      items: [
        {
          id: 'invite-1',
          organizationId: 'org-1',
          organizationName: 'Workspace',
          email: 'pending@example.com',
          role: 'viewer',
          status: 'pending',
          invitedByUserId: 'user-1',
          expiresAt: '2026-12-31T00:00:00Z',
          createdAt: '2026-01-01T00:00:00Z',
        },
      ],
    }),
  ),
  http.post('/api/organizations/:organizationId/invitations', async () =>
    HttpResponse.json({
      id: 'invite-2',
      organizationId: 'org-1',
      organizationName: 'Workspace',
      email: 'new@example.com',
      role: 'developer',
      status: 'pending',
      invitedByUserId: 'user-1',
      expiresAt: '2026-12-31T00:00:00Z',
      createdAt: '2026-01-02T00:00:00Z',
    }),
  ),
  http.delete('/api/organizations/:organizationId/invitations/:invitationId', async () =>
    new HttpResponse(null, { status: 204 }),
  ),
  http.get('/api/invitations/mine', async () => HttpResponse.json({ items: [] })),
  http.post('/api/organizations/:organizationId/transfer-ownership', async () =>
    HttpResponse.json({
      items: [
        {
          userId: 'user-2',
          organizationId: 'org-1',
          role: 'owner',
          email: 'dev@example.com',
          fullName: 'Developer',
        },
        {
          userId: 'user-1',
          organizationId: 'org-1',
          role: 'admin',
          email: 'user@example.com',
          fullName: 'Test User',
        },
      ],
    }),
  ),
  http.get('/api/simulations/throughput', async () =>
    HttpResponse.json({
      spinsPerSecond: 50000,
      sampleCount: 3,
      source: 'historical',
    }),
  ),
  http.post('/api/mathematics/calibrate', async () =>
    HttpResponse.json({
      theoreticalRtp: {
        totalRtp: 0.96,
        baseRtp: 0.1,
        scatterRtp: 0.86,
        lineRtp: 0,
        outcomeCount: 100,
        reelSetId: 'base',
      },
      featureProbabilities: [],
      calibration: {
        targetRtp: 96,
        theoreticalRtp: 96,
        simulatedRtp: 95.9,
        targetDelta: -0.1,
        theoryVsSimulationDelta: -0.1,
        withinTolerance: true,
        tolerance: 0.1,
      },
      discrepancy: {
        items: [
          {
            metric: 'RTP',
            theoretical: 0.96,
            simulated: 0.959,
            target: 0.96,
            delta: -0.001,
            status: 'PASS',
          },
          {
            metric: 'FREE_SPINS Frequency',
            theoretical: 0.04,
            simulated: 0.042,
            target: null,
            delta: 0.002,
            status: 'PASS',
          },
        ],
        summary: 'Within tolerance',
      },
      recommendations: [],
      engineVersion: 'runtime-core@1.8.0',
    }),
  ),
  http.get('/api/engine/version', async () =>
    HttpResponse.json({
      engineVersion: 'runtime-core@1.8.0',
      validatorVersion: 'validation-engine@1.0.0',
      supportedPlugins: [],
      rng: { algorithm: 'PCG64', policy: 'v1-hash-shard' },
      maxRecommendedSpinCount: 10_000_000,
      deploymentMode: 'mvp',
      maxSimulationSpinCount: 10_000_000,
      maxActiveSimulations: 2,
      activeSimulationCount: 0,
    }),
  ),
  http.get('/api/organizations/:organizationId', async () =>
    HttpResponse.json({
      id: 'org-1',
      name: 'Workspace',
      slug: 'workspace',
      createdAt: '2026-01-01T00:00:00Z',
      updatedAt: '2026-01-01T00:00:00Z',
    }),
  ),
  http.get('/api/notifications', async () =>
    HttpResponse.json({
      items: [
        {
          id: 'notif-1',
          type: 'simulation_completed',
          title: 'Simulation completed',
          message: 'Simulation sim-1 finished successfully.',
          organizationId: 'org-1',
          entityType: 'simulation',
          entityId: 'sim-1',
          readAt: null,
          createdAt: '2026-01-02T00:00:00Z',
        },
      ],
      total: 1,
      unreadCount: 1,
      page: 1,
      pageSize: 20,
    }),
  ),
  http.post('/api/notifications/:notificationId/read', async () =>
    HttpResponse.json({
      notificationId: 'notif-1',
      readAt: '2026-01-02T01:00:00Z',
    }),
  ),
  http.post('/api/notifications/read-all', async () =>
    HttpResponse.json({ updatedCount: 1 }),
  ),
  http.get('/api/audit', async () =>
    HttpResponse.json({
      items: [
        {
          id: 'audit-1',
          userId: 'user-1',
          userEmail: 'user@example.com',
          userName: 'Test User',
          organizationId: 'org-1',
          action: 'auth.login',
          entityType: 'user',
          entityId: 'user-1',
          metadata: null,
          createdAt: '2026-01-01T00:00:00Z',
        },
      ],
      total: 1,
      page: 1,
      pageSize: 20,
    }),
  ),
  http.get('/api/users/me/preferences', async () =>
    HttpResponse.json({
      theme: 'light',
      notifySimulationCompleted: true,
      notifySimulationFailed: true,
      notifyValidationFailed: true,
      notifyOrganizationInvitation: true,
    }),
  ),
  http.patch('/api/users/me/preferences', async ({ request }) =>
    HttpResponse.json(await request.json()),
  ),
  http.patch('/api/users/me/profile', async ({ request }) => {
    const body = (await request.json()) as { fullName?: string }
    return HttpResponse.json({
      ...user,
      fullName: body.fullName ?? user.fullName,
    })
  }),
  http.post('/api/users/me/change-password', async () =>
    new HttpResponse(null, { status: 204 }),
  ),
  http.get('/api/dashboard/summary', async () =>
    HttpResponse.json({
      totalGames: 25,
      totalSimulations: 12,
      activeSimulations: 1,
      averageRtp: 0.96,
      recentSimulations: [
        {
          simulationId: 'sim-1',
          gameVersionId: 'version-1',
          gameName: 'Lucky Stars',
          gameVersionLabel: 'v1',
          status: 'completed',
          workflowStatus: 'draft',
          spinCount: 1000,
          rtp: 0.96,
          withinRtpTolerance: true,
          createdAt: '2026-01-01T00:00:00Z',
        },
      ],
      outsideRtpTolerance: [],
      pendingReviews: [
        {
          simulationId: 'sim-review-1',
          workflowStatus: 'under_review',
          gameVersionId: 'version-1',
          updatedAt: '2026-01-03T00:00:00Z',
        },
      ],
      myPendingReviews: [
        {
          simulationId: 'sim-review-1',
          workflowStatus: 'under_review',
          gameVersionId: 'version-1',
          updatedAt: '2026-01-03T00:00:00Z',
        },
      ],
      certificationReady: [],
      recentlyApproved: [],
      recommendedActions: [
        {
          id: 'run-simulation',
          label: 'Run a calibration simulation',
          description: 'Upload a game version and start a 100K-spin simulation.',
          href: '/simulations/create',
        },
      ],
      recentNotifications: [
        {
          id: 'notif-1',
          type: 'simulation_completed',
          title: 'Simulation completed',
          message: 'Simulation sim-1 finished successfully.',
          organizationId: 'org-1',
          entityType: 'simulation',
          entityId: 'sim-1',
          readAt: null,
          createdAt: '2026-01-02T00:00:00Z',
        },
      ],
      recentActivity: [
        {
          id: 'audit-1',
          userId: 'user-1',
          userEmail: 'user@example.com',
          userName: 'Test User',
          organizationId: 'org-1',
          action: 'auth.login',
          entityType: 'user',
          entityId: 'user-1',
          metadata: null,
          createdAt: '2026-01-01T00:00:00Z',
        },
      ],
    }),
  ),
  http.get('/api/simulations/:simulationId/export', async () =>
    HttpResponse.json({ simulationId: 'sim-1', summary: { rtp: 0.96 } }),
  ),
  http.get('/api/games/:gameId/versions/:versionId/export', async () =>
    HttpResponse.json({ schemaVersion: '1.0.0' }),
  ),
  http.get('/api/metrics', async () =>
    new HttpResponse(
      '# HELP api_requests_total Total API HTTP requests\napi_requests_total{method="GET",path="/health",status="200"} 3\nsimulations_total{status="completed"} 2\nsimulation_worker_queue_size 0\n',
      { headers: { 'Content-Type': 'text/plain' } },
    ),
  ),
]

export const server = setupServer(...handlers)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
