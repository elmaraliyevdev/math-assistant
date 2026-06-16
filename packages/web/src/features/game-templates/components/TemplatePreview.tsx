import { JsonViewer } from '@/features/games/components'
import type { GameTemplate } from '@/features/game-templates/types'

export function TemplatePreview({ template }: { template: GameTemplate }) {
  return <JsonViewer value={template.canonicalJson} />
}
