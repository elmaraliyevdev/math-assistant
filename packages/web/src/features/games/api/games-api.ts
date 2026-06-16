import { api } from '@/services/api'
import type {
  CreateGameVersionResult,
  CreateGameInput,
  CreateGameVersionInput,
  UpdateGameInput,
} from '@/features/games/types'
import type {
  Game,
  GameListResponse,
  GameVersionDetail,
  GameVersionSummary,
  PaginationParams,
} from '@/types/api'

export const gamesApi = {
  list(params: PaginationParams = {}): Promise<GameListResponse> {
    return api.get<GameListResponse>('/games', { params }).then((r) => r.data)
  },

  get(gameId: string): Promise<Game> {
    return api.get<Game>(`/games/${gameId}`).then((r) => r.data)
  },

  create(input: CreateGameInput): Promise<Game> {
    return api.post<Game>('/games', input).then((r) => r.data)
  },

  update(gameId: string, input: UpdateGameInput): Promise<Game> {
    return api.patch<Game>(`/games/${gameId}`, input).then((r) => r.data)
  },

  remove(gameId: string): Promise<void> {
    return api.delete(`/games/${gameId}`).then(() => undefined)
  },

  listVersions(gameId: string): Promise<GameVersionSummary[]> {
    return api
      .get<GameVersionSummary[]>(`/games/${gameId}/versions`)
      .then((r) => r.data)
  },

  getVersion(gameId: string, versionId: string): Promise<GameVersionDetail> {
    return api
      .get<GameVersionDetail>(`/games/${gameId}/versions/${versionId}`)
      .then((r) => r.data)
  },

  createVersion(
    gameId: string,
    input: CreateGameVersionInput,
  ): Promise<CreateGameVersionResult> {
    return api
      .post<CreateGameVersionResult>(`/games/${gameId}/versions`, input)
      .then((r) => r.data)
  },
}
