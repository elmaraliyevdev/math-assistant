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
import { ForgotPasswordPage } from '@/pages/auth/forgot-password'
import { ResetPasswordPage } from '@/pages/auth/reset-password'
import { VerifyEmailPage } from '@/pages/auth/verify-email'
import { DashboardPage } from '@/pages/dashboard/index'
import { GameCreatePage } from '@/pages/games/create'
import { GameDetailPage } from '@/pages/games/detail'
import { GameVersionDetailPage } from '@/pages/games/version-detail'
import { GamesListPage } from '@/pages/games/list'
import { OnboardingPage } from '@/pages/onboarding/index'
import { ReelStudioLandingPage } from '@/pages/reel-studio/index'
import { ReelStudioVersionPage } from '@/pages/reel-studio/version'
import { SettingsPage } from '@/pages/settings/index'
import { TemplatesPage } from '@/pages/templates/index'
import { AssistantPage } from '@/pages/assistant/index'
import { MathematicsPage } from '@/pages/mathematics/index'
import { SimulationCreatePage } from '@/pages/simulations/create'
import { SimulationsComparePage } from '@/pages/simulations/compare'
import { SimulationDetailPage } from '@/pages/simulations/detail'
import { SimulationReviewPage } from '@/pages/simulations/review'
import { SimulationsListPage } from '@/pages/simulations/list'
import { DemoPage } from '@/pages/demo/index'
import { AdminContactPage } from '@/pages/admin/contact-submissions'

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

const forgotPasswordRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/forgot-password',
  component: ForgotPasswordPage,
})

const resetPasswordRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/reset-password',
  component: ResetPasswordPage,
  validateSearch: (search: Record<string, unknown>) => ({
    token: typeof search.token === 'string' ? search.token : undefined,
  }),
})

const verifyEmailRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/verify-email',
  component: VerifyEmailPage,
  validateSearch: (search: Record<string, unknown>) => ({
    token: typeof search.token === 'string' ? search.token : undefined,
  }),
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

const reelStudioRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/reel-studio',
  component: ReelStudioLandingPage,
})

const reelStudioVersionRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/games/$gameId/versions/$versionId/reel-studio',
  component: ReelStudioVersionPage,
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
  beforeLoad: () => {
    throw redirect({ to: '/settings', search: { section: 'team' } })
  },
})

const auditRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/audit',
  beforeLoad: () => {
    throw redirect({ to: '/settings', search: { section: 'audit' } })
  },
})

const settingsRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/settings',
  component: SettingsPage,
})

const demoRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/demo',
  component: DemoPage,
})

const adminContactRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/admin/contact',
  component: AdminContactPage,
})

const routeTree = rootRoute.addChildren([
  indexRoute,
  loginRoute,
  registerRoute,
  forgotPasswordRoute,
  resetPasswordRoute,
  verifyEmailRoute,
  protectedRoute.addChildren([
    onboardingRoute,
    dashboardRoute,
    gamesRoute,
    gameCreateRoute,
    gameDetailRoute,
    gameVersionDetailRoute,
    reelStudioRoute,
    reelStudioVersionRoute,
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
    demoRoute,
    adminContactRoute,
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
