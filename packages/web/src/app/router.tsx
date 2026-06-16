import {
  createRootRoute,
  createRoute,
  createRouter,
  Outlet,
  redirect,
} from '@tanstack/react-router'

import { AppLayout } from '@/app/layout'
import { useAuthStore } from '@/stores/auth-store'
import { LoginPage } from '@/pages/auth/login'
import { RegisterPage } from '@/pages/auth/register'
import { DashboardPage } from '@/pages/dashboard/index'
import { GameCreatePage } from '@/pages/games/create'
import { GameDetailPage } from '@/pages/games/detail'
import { GameVersionDetailPage } from '@/pages/games/version-detail'
import { GamesListPage } from '@/pages/games/list'
import { OrganizationSettingsPage } from '@/pages/organizations/settings'
import { OnboardingPage } from '@/pages/onboarding/index'
import { AuditPage } from '@/pages/audit/index'
import { SettingsPage } from '@/pages/settings/index'
import { TemplatesPage } from '@/pages/templates/index'
import { AssistantPage } from '@/pages/assistant/index'
import { MathematicsPage } from '@/pages/mathematics/index'
import { SimulationCreatePage } from '@/pages/simulations/create'
import { SimulationsComparePage } from '@/pages/simulations/compare'
import { SimulationDetailPage } from '@/pages/simulations/detail'
import { SimulationReviewPage } from '@/pages/simulations/review'
import { SimulationsListPage } from '@/pages/simulations/list'

function RootComponent() {
  return <Outlet />
}

const rootRoute = createRootRoute({
  component: RootComponent,
})

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  beforeLoad: () => {
    if (useAuthStore.getState().isAuthenticated()) {
      throw redirect({ to: '/dashboard' })
    }
    throw redirect({ to: '/login' })
  },
})

const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/login',
  component: LoginPage,
  beforeLoad: () => {
    if (useAuthStore.getState().isAuthenticated()) {
      throw redirect({ to: '/dashboard' })
    }
  },
})

const registerRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/register',
  component: RegisterPage,
  beforeLoad: () => {
    if (useAuthStore.getState().isAuthenticated()) {
      throw redirect({ to: '/dashboard' })
    }
  },
})

const protectedRoute = createRoute({
  getParentRoute: () => rootRoute,
  id: 'protected',
  component: AppLayout,
  beforeLoad: () => {
    if (!useAuthStore.getState().isAuthenticated()) {
      throw redirect({ to: '/login' })
    }
  },
})

const onboardingRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/onboarding',
  component: OnboardingPage,
})

const dashboardRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/dashboard',
  component: DashboardPage,
})

const gamesRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/games',
  component: GamesListPage,
})

const gameCreateRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/games/create',
  component: GameCreatePage,
})

const gameDetailRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/games/$gameId',
  component: GameDetailPage,
})

const gameVersionDetailRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/games/$gameId/versions/$versionId',
  component: GameVersionDetailPage,
})

const templatesRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/templates',
  component: TemplatesPage,
})

const assistantRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/assistant',
  component: AssistantPage,
})

const mathematicsRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/mathematics',
  component: MathematicsPage,
})

const simulationsRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/simulations',
  component: SimulationsListPage,
})

const simulationCreateRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/simulations/create',
  component: SimulationCreatePage,
})

const simulationCompareRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/simulations/compare',
  component: SimulationsComparePage,
})

const simulationDetailRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/simulations/$simulationId',
  component: SimulationDetailPage,
})

const simulationReviewRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/simulations/$simulationId/review',
  component: SimulationReviewPage,
})

const organizationSettingsRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/organizations/settings',
  component: OrganizationSettingsPage,
})

const auditRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/audit',
  component: AuditPage,
})

const settingsRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/settings',
  component: SettingsPage,
})

const routeTree = rootRoute.addChildren([
  indexRoute,
  loginRoute,
  registerRoute,
  protectedRoute.addChildren([
    onboardingRoute,
    dashboardRoute,
    gamesRoute,
    gameCreateRoute,
    gameDetailRoute,
    gameVersionDetailRoute,
    templatesRoute,
    mathematicsRoute,
    assistantRoute,
    simulationsRoute,
    simulationCreateRoute,
    simulationCompareRoute,
    simulationDetailRoute,
    simulationReviewRoute,
    organizationSettingsRoute,
    auditRoute,
    settingsRoute,
  ]),
])

export const router = createRouter({
  routeTree,
  defaultPreload: 'intent',
})

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
