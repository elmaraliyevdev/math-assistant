import type {
  AssistantSection,
  CalibrationRecommendation,
  GroundedCitation,
} from '@/types/api'

export type AssistantMode = 'simulation' | 'compare' | 'game-version'

export interface AssistantContextState {
  mode: AssistantMode
  gameId: string
  gameVersionId: string
  simulationId: string
  compareIds: string[]
}

export interface AssistantChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  sections?: AssistantSection[]
  citations?: GroundedCitation[]
  recommendations?: CalibrationRecommendation[]
  followUps?: string[]
  isStreaming?: boolean
}

export interface AssistantConversation {
  id: string
  title: string
  createdAt: string
  updatedAt: string
  context: AssistantContextState
  messages: AssistantChatMessage[]
}

export const DEFAULT_CONTEXT: AssistantContextState = {
  mode: 'simulation',
  gameId: '',
  gameVersionId: '',
  simulationId: '',
  compareIds: [],
}
