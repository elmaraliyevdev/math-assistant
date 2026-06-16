import { api } from '@/services/api'
import type {
  SimulationCompareResponse,
  SimulationDetail,
  SimulationListResponse,
  SimulationNote,
  SimulationNoteListResponse,
  SimulationResults,
  SimulationThroughput,
} from '@/types/api'

import type {
  CreateSimulationInput,
  SimulationListParams,
} from '@/features/simulations/types'

export const simulationsApi = {
  async list(params: SimulationListParams = {}): Promise<SimulationListResponse> {
    const { data } = await api.get<SimulationListResponse>('/simulations', {
      params,
    })
    return data
  },

  async get(simulationId: string): Promise<SimulationDetail> {
    const { data } = await api.get<SimulationDetail>(
      `/simulations/${simulationId}`,
    )
    return data
  },

  async getResults(simulationId: string): Promise<SimulationResults> {
    const { data } = await api.get<SimulationResults>(
      `/simulations/${simulationId}/results`,
    )
    return data
  },

  async create(input: CreateSimulationInput): Promise<{
    simulationId: string
    status: string
  }> {
    const { data } = await api.post<{ simulationId: string; status: string }>(
      '/simulations',
      input,
    )
    return data
  },

  async cancel(simulationId: string): Promise<{
    simulationId: string
    status: string
    cancelRequested: boolean
  }> {
    const { data } = await api.post<{
      simulationId: string
      status: string
      cancelRequested: boolean
    }>(`/simulations/${simulationId}/cancel`)
    return data
  },

  async compare(simulationIds: string[]): Promise<SimulationCompareResponse> {
    const { data } = await api.get<SimulationCompareResponse>(
      '/simulations/compare',
      { params: { ids: simulationIds.join(',') } },
    )
    return data
  },

  async getThroughput(): Promise<SimulationThroughput> {
    const { data } = await api.get<SimulationThroughput>('/simulations/throughput')
    return data
  },

  async listNotes(simulationId: string): Promise<SimulationNoteListResponse> {
    const { data } = await api.get<SimulationNoteListResponse>(
      `/simulations/${simulationId}/notes`,
    )
    return data
  },

  async createNote(
    simulationId: string,
    content: string,
  ): Promise<SimulationNote> {
    const { data } = await api.post<SimulationNote>(
      `/simulations/${simulationId}/notes`,
      { content },
    )
    return data
  },

  async deleteNote(simulationId: string, noteId: string): Promise<void> {
    await api.delete(`/simulations/${simulationId}/notes/${noteId}`)
  },
}
