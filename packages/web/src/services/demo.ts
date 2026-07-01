import { api } from '@/services/api'

export interface DemoGameSummary {
  id: string
  name: string
  versionCount: number
  simulationCount: number
}

export interface DemoOverview {
  configured?: boolean
  organizationId?: string
  organizationName: string
  gameCount: number
  versionCount: number
  simulationCount: number
  games: DemoGameSummary[]
}

export interface DuplicateDemoResult {
  gamesCopied: number
  organizationId: string
}

export const demoService = {
  async getOverview(): Promise<DemoOverview> {
    const { data } = await api.get<DemoOverview>('/demo/overview')
    return data
  },

  async duplicateToWorkspace(): Promise<DuplicateDemoResult> {
    const { data } = await api.post<DuplicateDemoResult>('/demo/duplicate')
    return data
  },
}
