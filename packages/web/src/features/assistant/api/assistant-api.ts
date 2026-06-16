import { api } from '@/services/api'
import type {
  GameVersionExplainResponse,
  SimulationAnalysisResponse,
  SimulationCompareAssistantResponse,
  SimulationRecommendResponse,
} from '@/types/api'

export const assistantApi = {
  async analyzeSimulation(simulationId: string): Promise<SimulationAnalysisResponse> {
    const { data } = await api.post<SimulationAnalysisResponse>(
      `/ai/simulations/${simulationId}/analyze`,
    )
    return data
  },

  async recommendSimulation(
    simulationId: string,
    targetRtp?: number,
  ): Promise<SimulationRecommendResponse> {
    const { data } = await api.post<SimulationRecommendResponse>(
      `/ai/simulations/${simulationId}/recommend`,
      targetRtp !== undefined ? { targetRtp } : {},
    )
    return data
  },

  async compareSimulations(
    simulationIds: string[],
  ): Promise<SimulationCompareAssistantResponse> {
    const { data } = await api.post<SimulationCompareAssistantResponse>(
      '/ai/simulations/compare',
      { simulationIds },
    )
    return data
  },

  async explainGameVersion(gameVersionId: string): Promise<GameVersionExplainResponse> {
    const { data } = await api.post<GameVersionExplainResponse>(
      `/ai/game-versions/${gameVersionId}/explain`,
    )
    return data
  },
}
