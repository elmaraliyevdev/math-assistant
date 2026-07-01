import { api } from '@/services/api'
import { mergeReelSetsIntoCanonical } from '@/features/reel-studio/lib/serialize-canonical'
import type { StudioReelSet } from '@/features/reel-studio/types'

export interface MergeReelStudioRequest {
  canonicalJson: Record<string, unknown>
  reelSets: Record<string, StudioReelSet>
}

export interface MergeReelStudioResponse {
  canonicalJson: Record<string, unknown>
}

export interface ValidateGameResponse {
  contentHash?: string
  engineVersion?: string
  report?: { passed: boolean; findings: unknown[] }
}

export const reelStudioApi = {
  merge(body: MergeReelStudioRequest): Promise<MergeReelStudioResponse> {
    return api
      .post<MergeReelStudioResponse>('/reel-studio/merge', {
        canonicalJson: body.canonicalJson,
        reelSets: body.reelSets,
      })
      .then((response) => response.data)
  },

  validate(canonicalJson: Record<string, unknown>, engineVersion: string) {
    return api
      .post<ValidateGameResponse>('/games/validate', {
        canonicalJson,
        engineVersion,
      })
      .then((response) => response.data)
  },

  buildPreview(
    originalCanonicalJson: Record<string, unknown>,
    reelSets: Record<string, StudioReelSet>,
  ): Record<string, unknown> {
    return mergeReelSetsIntoCanonical(originalCanonicalJson, reelSets)
  },
}
