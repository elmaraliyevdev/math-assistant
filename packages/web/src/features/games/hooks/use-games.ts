import {
  useMutation,
  useQuery,
  useQueryClient,
  type QueryKey,
} from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'

import { gamesApi } from '@/features/games/api/games-api'
import type {
  CreateGameInput,
  CreateGameVersionInput,
  UpdateGameInput,
} from '@/features/games/types'
import { getApiErrorCode, parseApiError } from '@/lib/api-error'
import { toast } from '@/lib/toast'
import { getErrorMessage } from '@/services/api'
import type { Game, GameListResponse, PaginationParams } from '@/types/api'

export const gameKeys = {
  all: ['games'] as const,
  list: (params: PaginationParams) => ['games', 'list', params] as const,
  detail: (gameId: string) => ['games', 'detail', gameId] as const,
  versions: (gameId: string) => ['games', gameId, 'versions'] as const,
  version: (gameId: string, versionId: string) =>
    ['games', gameId, 'versions', versionId] as const,
}

export function useGames(params: PaginationParams = {}) {
  return useQuery({
    queryKey: gameKeys.list(params),
    queryFn: () => gamesApi.list(params),
  })
}

export function useGame(gameId: string) {
  return useQuery({
    queryKey: gameKeys.detail(gameId),
    queryFn: () => gamesApi.get(gameId),
    enabled: Boolean(gameId),
  })
}

export function useGameVersions(gameId: string) {
  return useQuery({
    queryKey: gameKeys.versions(gameId),
    queryFn: () => gamesApi.listVersions(gameId),
    enabled: Boolean(gameId),
  })
}

export function useGameVersion(gameId: string, versionId: string) {
  return useQuery({
    queryKey: gameKeys.version(gameId, versionId),
    queryFn: () => gamesApi.getVersion(gameId, versionId),
    enabled: Boolean(gameId) && Boolean(versionId),
  })
}

export function useCreateGame(options?: { suppressNavigation?: boolean }) {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const suppressNavigation = options?.suppressNavigation ?? false

  return useMutation({
    mutationFn: (input: CreateGameInput) => gamesApi.create(input),
    onSuccess: async (game) => {
      await queryClient.invalidateQueries({ queryKey: gameKeys.all })
      toast.success('Game created successfully')
      if (suppressNavigation) {
        return
      }
      await navigate({ to: '/games/$gameId', params: { gameId: game.id } })
    },
    onError: (error) => {
      toast.error(getErrorMessage(error))
    },
  })
}

export function useUpdateGame(gameId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (input: UpdateGameInput) => gamesApi.update(gameId, input),
    onMutate: async (input) => {
      await queryClient.cancelQueries({ queryKey: gameKeys.detail(gameId) })
      const previous = queryClient.getQueryData<Game>(gameKeys.detail(gameId))
      if (previous) {
        queryClient.setQueryData<Game>(gameKeys.detail(gameId), {
          ...previous,
          ...input,
          description: input.description ?? previous.description,
        })
      }
      return { previous }
    },
    onError: (error, _input, context) => {
      if (context?.previous) {
        queryClient.setQueryData(gameKeys.detail(gameId), context.previous)
      }
      toast.error(getErrorMessage(error))
    },
    onSuccess: async () => {
      toast.success('Game updated')
      await queryClient.invalidateQueries({ queryKey: gameKeys.all })
      await queryClient.invalidateQueries({ queryKey: gameKeys.detail(gameId) })
    },
  })
}

export function useDeleteGame() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: (gameId: string) => gamesApi.remove(gameId),
    onMutate: async (gameId) => {
      await queryClient.cancelQueries({ queryKey: gameKeys.all })
      const listQueries = queryClient.getQueriesData<GameListResponse>({
        queryKey: gameKeys.all,
      })
      const snapshots: Array<[QueryKey, GameListResponse | undefined]> = []
      for (const [key, data] of listQueries) {
        snapshots.push([key, data])
        if (data) {
          queryClient.setQueryData<GameListResponse>(key, {
            ...data,
            items: data.items.filter((game) => game.id !== gameId),
            total: Math.max(0, data.total - 1),
          })
        }
      }
      return { snapshots }
    },
    onError: (error, _gameId, context) => {
      context?.snapshots.forEach(([key, data]) => {
        queryClient.setQueryData(key, data)
      })
      toast.error(getErrorMessage(error))
    },
    onSuccess: async () => {
      toast.success('Game deleted')
      await queryClient.invalidateQueries({ queryKey: gameKeys.all })
      await navigate({ to: '/games' })
    },
  })
}

export type CreateVersionNavigateTo = 'game' | 'version'

export function useCreateGameVersion(
  gameId: string,
  options?: { navigateTo?: CreateVersionNavigateTo; suppressNavigation?: boolean },
) {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const navigateTo = options?.navigateTo ?? 'version'
  const suppressNavigation = options?.suppressNavigation ?? false

  return useMutation({
    mutationFn: (input: CreateGameVersionInput) =>
      gamesApi.createVersion(gameId, input),
    onSuccess: async (result) => {
      toast.success(
        `Version ${result.version} created — validation passed (${result.validationSummary.findingCount} findings)`,
      )
      await queryClient.invalidateQueries({ queryKey: gameKeys.versions(gameId) })
      await queryClient.invalidateQueries({ queryKey: gameKeys.detail(gameId) })
      await queryClient.invalidateQueries({ queryKey: gameKeys.all })
      if (suppressNavigation) {
        return
      }
      if (navigateTo === 'game') {
        await navigate({ to: '/games/$gameId', params: { gameId } })
      } else {
        await navigate({
          to: '/games/$gameId/versions/$versionId',
          params: { gameId, versionId: result.id },
        })
      }
    },
    onError: (error) => {
      const code = getApiErrorCode(error)
      if (code === 'DUPLICATE_GAME_VERSION') {
        return
      }
      if (code !== 'VALIDATION_FAILED') {
        toast.error(getErrorMessage(error))
      }
    },
  })
}

export interface DuplicateVersionDetails {
  contentHash?: string
  existingVersionId: string
  existingVersionName: string
  existingGameId: string
  existingGameName: string
  createdAt: string
}

export function getDuplicateVersionDetails(
  error: unknown,
): DuplicateVersionDetails | null {
  const apiError = parseApiError(error)
  if (apiError?.code !== 'DUPLICATE_GAME_VERSION' || !apiError.details) {
    return null
  }
  const details = apiError.details
  if (
    typeof details.existingVersionId !== 'string' ||
    typeof details.existingVersionName !== 'string' ||
    typeof details.existingGameId !== 'string' ||
    typeof details.existingGameName !== 'string' ||
    typeof details.createdAt !== 'string'
  ) {
    return null
  }
  return {
    contentHash:
      typeof details.contentHash === 'string' ? details.contentHash : undefined,
    existingVersionId: details.existingVersionId,
    existingVersionName: details.existingVersionName,
    existingGameId: details.existingGameId,
    existingGameName: details.existingGameName,
    createdAt: details.createdAt,
  }
}
