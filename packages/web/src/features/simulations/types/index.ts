import type {
  SimulationDetail,
  SimulationResults,
  SimulationSummary,
} from '@/types/api'

export type {
  SimulationDetail,
  SimulationResults,
  SimulationSummary,
}

export interface SimulationListParams {
  page?: number
  pageSize?: number
  status?: string
  gameVersionId?: string
}

export interface CreateSimulationInput {
  gameVersionId: string
  spinCount: number
  masterSeed?: string
  eventLogMode?: string
  betMinorUnits?: number
}

export interface SimulationTableRow extends SimulationSummary {
  gameName: string
  gameId: string | null
  versionNumber: number | null
  organizationName: string
  rtp: number | null
  rtpDeviation: number | null
  totalBetMinorUnits: number | null
  totalWinMinorUnits: number | null
}
