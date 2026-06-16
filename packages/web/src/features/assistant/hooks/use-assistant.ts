import { useMutation } from '@tanstack/react-query'

import { assistantApi } from '@/features/assistant/api/assistant-api'

export function useAnalyzeSimulation() {
  return useMutation({
    mutationFn: (simulationId: string) => assistantApi.analyzeSimulation(simulationId),
  })
}

export function useRecommendSimulation() {
  return useMutation({
    mutationFn: ({
      simulationId,
      targetRtp,
    }: {
      simulationId: string
      targetRtp?: number
    }) => assistantApi.recommendSimulation(simulationId, targetRtp),
  })
}

export function useCompareSimulationsAssistant() {
  return useMutation({
    mutationFn: (simulationIds: string[]) =>
      assistantApi.compareSimulations(simulationIds),
  })
}

export function useExplainGameVersion() {
  return useMutation({
    mutationFn: (gameVersionId: string) =>
      assistantApi.explainGameVersion(gameVersionId),
  })
}
