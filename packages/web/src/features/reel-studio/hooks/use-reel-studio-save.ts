import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'

import { gameKeys } from '@/features/games/hooks/use-games'
import { getDuplicateVersionDetails } from '@/features/games/hooks/use-games'
import { gamesApi } from '@/features/games/api/games-api'
import { mergeReelSetsIntoCanonical } from '@/features/reel-studio/lib/serialize-canonical'
import type { ReelStudioDocument } from '@/features/reel-studio/types'
import { getApiErrorCode } from '@/lib/api-error'
import { getErrorMessage } from '@/services/api'
import { toast } from '@/lib/toast'

export function useReelStudioSave(gameId: string) {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: async (document: ReelStudioDocument) => {
      const canonicalJson = mergeReelSetsIntoCanonical(
        document.originalCanonicalJson,
        document.reelSets,
      )
      return gamesApi.createVersion(gameId, {
        canonicalJson,
        engineVersion: document.engineVersion,
      })
    },
    onSuccess: async (result) => {
      toast.success(`Saved as version ${result.version}`)
      await queryClient.invalidateQueries({ queryKey: gameKeys.versions(gameId) })
      await queryClient.invalidateQueries({ queryKey: gameKeys.detail(gameId) })
      await navigate({
        to: '/games/$gameId/versions/$versionId/reel-studio',
        params: { gameId, versionId: result.id },
      })
    },
    onError: async (error) => {
      const duplicate = getDuplicateVersionDetails(error)
      if (duplicate) {
        toast.info('This version already exists — opening it instead.')
        await navigate({
          to: '/games/$gameId/versions/$versionId/reel-studio',
          params: {
            gameId: duplicate.existingGameId,
            versionId: duplicate.existingVersionId,
          },
        })
        return
      }
      const code = getApiErrorCode(error)
      if (code !== 'VALIDATION_FAILED') {
        toast.error(getErrorMessage(error))
      }
    },
  })
}
