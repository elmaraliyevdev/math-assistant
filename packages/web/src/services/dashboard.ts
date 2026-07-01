import { api } from '@/services/api'

import type { DashboardSummary } from '@/services/dashboard-types'

export type {
  DashboardRecommendedAction,
  DashboardSimulationSummary,
  DashboardSummary,
} from '@/services/dashboard-types'

export const dashboardApi = {
  getSummary() {
    return api
      .get<DashboardSummary>('/dashboard/summary')
      .then((r) => r.data)
  },
}
