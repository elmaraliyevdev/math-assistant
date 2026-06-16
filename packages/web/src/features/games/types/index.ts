import type {
  CreateGameVersionResponse,
  Game,
  GameListResponse,
  GameVersionDetail,
  GameVersionSummary,
  PaginationParams,
} from '@/types/api'

export type { Game, GameListResponse, GameVersionDetail, GameVersionSummary, PaginationParams }

export interface CreateGameInput {
  name: string
  description?: string
  organizationId: string
}

export interface UpdateGameInput {
  name?: string
  description?: string | null
}

export interface CreateGameVersionInput {
  canonicalJson: Record<string, unknown>
  engineVersion: string
}

export type CreateGameVersionResult = CreateGameVersionResponse

export interface ValidationFinding {
  code: string
  severity: string
  message: string
  path: string
  suggestion?: string | null
}

export interface GameTableRow extends Game {
  versionCount: number
  organizationName: string
}
