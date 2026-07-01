import { api } from '@/services/api'
import type {
  ConstraintDocument,
  ConstraintPreset,
  ConstraintValidationReport,
} from '@/features/reel-studio/constraints/types'
import type { StudioReelSet } from '@/features/reel-studio/types'
import type { StudioSymbol } from '@/features/reel-studio/types'

export const constraintsApi = {
  validate(
    reelSet: StudioReelSet,
    symbols: Record<string, StudioSymbol>,
    constraintDocument: ConstraintDocument,
  ): Promise<ConstraintValidationReport> {
    return api
      .post<ConstraintValidationReport>('/reel-studio/constraints/validate', {
        reelSet,
        symbols,
        constraintDocument,
      })
      .then((response) => response.data)
  },

  listPresets(): Promise<ConstraintPreset[]> {
    return api.get<ConstraintPreset[]>('/reel-studio/constraints/presets').then((r) => r.data)
  },

  savePreset(preset: ConstraintPreset): Promise<ConstraintPreset> {
    return api
      .post<ConstraintPreset>('/reel-studio/constraints/presets', { preset })
      .then((r) => r.data)
  },
}
