import { useMemo } from 'react'

import {
  GAME_TEMPLATES,
  getTemplateById,
} from '@/features/game-templates/api/templates-api'

export const templateKeys = {
  all: ['game-templates'] as const,
}

export function useGameTemplates() {
  return useMemo(() => GAME_TEMPLATES, [])
}

export function useGameTemplate(templateId: string | undefined) {
  return useMemo(
    () => (templateId ? getTemplateById(templateId) : undefined),
    [templateId],
  )
}
