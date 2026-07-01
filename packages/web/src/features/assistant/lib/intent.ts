import type {
  GameVersionExplainResponse,
  SimulationAnalysisResponse,
  SimulationCompareAssistantResponse,
  SimulationRecommendResponse,
} from '@/types/api'

export function parseTargetRtp(message: string): number | undefined {
  const match = message.match(/(\d{1,3}(?:\.\d+)?)\s*%?/)
  if (!match) return undefined
  const value = Number(match[1])
  return Number.isFinite(value) ? value : undefined
}

export function isRecommendIntent(message: string) {
  const lower = message.toLowerCase()
  return (
    lower.includes('recommend') ||
    lower.includes('tuning') ||
    lower.includes('calibrat') ||
    lower.includes('optimize') ||
    lower.includes('improve')
  )
}

export function isCompareIntent(message: string) {
  const lower = message.toLowerCase()
  return lower.includes('compare') || lower.includes('versus') || lower.includes(' vs ')
}

export function isExplainIntent(message: string) {
  const lower = message.toLowerCase()
  return lower.includes('explain') || lower.includes('why') || lower.includes('describe')
}

export type AssistantApiResult =
  | SimulationAnalysisResponse
  | SimulationRecommendResponse
  | SimulationCompareAssistantResponse
  | GameVersionExplainResponse

export function toAssistantMessage(result: AssistantApiResult) {
  const recommendations =
    'recommendations' in result && Array.isArray(result.recommendations)
      ? result.recommendations
      : undefined

  return {
    content: result.content,
    sections: result.sections,
    citations: result.citations,
    recommendations,
  }
}
